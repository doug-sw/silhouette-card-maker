from pathlib import Path
from base64 import b64decode
import requests
from filetype.filetype import guess_extension
from silhouette_card_maker.models import Card, CardSide, Status
from silhouette_card_maker.fetchers.base import BaseCardImageFetcher
from silhouette_card_maker.utils import remove_nonalphanumeric
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

MPCFILL_REQUEST_URL = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="

class MPCFillCardImageFetcher(BaseCardImageFetcher):
    HEADERS = {
        "user-agent": "silhouette-card-maker/0.1",
        "accept": "*/*",
    }

    def fetch_card(self, card: Card, output_dir: Path) -> Status:
        output_dir = Path(output_dir)
        status_front = self.download_image(card, CardSide.FRONT, output_dir / "front")
        status_back = Status.SUCCESS
        if card.id_back:
            status_back = self.download_image(card, CardSide.BACK, output_dir / "double_sided")
        return Status.FAIL if Status.FAIL in (status_front, status_back) else Status.SUCCESS

    def download_image(self, card: Card, side: CardSide, output_dir: Path) -> Status:
        if side is CardSide.FRONT:
            card_id = card.id_front
        elif side is CardSide.BACK:
            if not card.id_back:
                return Status.SUCCESS
            card_id = card.id_back
        else:
            raise ValueError(f"Unhandled card side {side}")

        print(f"{card.index} download ({side.name.lower()}) started.")
        try:
            resp = self._request(card_id)
        except requests.RequestException:
            return Status.FAIL

        if not resp.content:
            return Status.FAIL

        try:
            image_bytes = b64decode(resp.content)
        except Exception:
            return Status.FAIL

        file_ext = guess_extension(image_bytes)
        if not file_ext:
            return Status.FAIL

        safe_name = remove_nonalphanumeric(card.name)
        for counter in range(1, card.quantity + 1):
            filename = f"{card.index}{safe_name}{counter}.{file_ext}"
            filepath = output_dir / filename
            filepath.write_bytes(image_bytes)

        return Status.SUCCESS

    def _request(self, card_id: str, retries: int = 3) -> requests.Response:
        for attempt in range(retries):
            try:
                resp = requests.get(MPCFILL_REQUEST_URL + card_id, headers=self.HEADERS)
                resp.raise_for_status()
                return resp
            except requests.RequestException:
                if attempt == retries - 1:
                    raise

    @classmethod
    def fetch_cards_parallel(cls, cards, output_dir: Path, max_workers: int | None = None) -> None:
        output_dir = Path(output_dir)
        if max_workers == 1 or len(cards) < 2:
            cls().fetch_cards(cards, output_dir)
            return

        fetcher = cls()
        results: list[Status] = [Status.FAIL] * len(cards)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {executor.submit(fetcher.fetch_card, card, output_dir): i for i, card in enumerate(cards)}
            for future in as_completed(future_to_index):
                i = future_to_index[future]
                try:
                    results[i] = future.result()
                except Exception:
                    traceback.print_exc()
                    results[i] = Status.FAIL

        cls.log_failures(cards, results)

    @staticmethod
    def log_failures(cards, statuses):
        success_count = sum(s is Status.SUCCESS for s in statuses)
        fail_count = sum(s is Status.FAIL for s in statuses)
        print(f"Successfully downloaded {success_count}/{len(cards)} images.")
        if fail_count:
            print(f"Failed to download {fail_count} images:")
            for card, status in zip(cards, statuses):
                if status is Status.FAIL:
                    print(f"\tCard: {card.name}")
