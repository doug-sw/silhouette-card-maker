import os
from base64 import b64decode
import requests
from filetype.filetype import guess_extension
from common import remove_nonalphanumeric
from xml.etree import ElementTree as ET
from pathlib import Path
import traceback
import enum
import concurrent.futures
from dataclasses import dataclass
from typing import Optional
MPCFILL_REQUEST_URL = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="


class Status(enum.Enum):
    SUCCESS = enum.auto()
    FAIL = enum.auto()

@dataclass
class Card:
    name: str
    index: int
    id_front: str
    id_back: Optional[str] = None
    quantity: int = 1

class CardSide(enum.Enum):
    FRONT = enum.auto()
    BACK = enum.auto()

class MPCFillCardImageFetcher:
    BASE_URL = MPCFILL_REQUEST_URL
    HEADERS = {
        "user-agent": "silhouette-card-maker/0.1",
        "accept": "*/*"
    }

    def fetch_card(self, card: Card, output_dir: Path) -> Status:
        output_dir = Path(output_dir)

        status_front = self.download_image(card, CardSide.FRONT, output_dir / "front")

        status_back = Status.SUCCESS
        if card.id_back:
            status_back = self.download_image(card, CardSide.BACK, output_dir / "double_sided")
            
        return Status.FAIL if Status.FAIL in (status_front, status_back) else Status.SUCCESS

    def _request(self, card_id: str, retries: int = 3) -> requests.Response:
        for attempt in range(retries):
            try:
                resp = requests.get(self.BASE_URL + card_id, headers=self.HEADERS)
                resp.raise_for_status()
                return resp
            except requests.RequestException:
                if attempt == retries - 1:
                    raise

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
            filename = f'{card.index}{safe_name}{counter}.{file_ext}'
            filepath = Path(output_dir) / filename
            filepath.write_bytes(image_bytes)

        return Status.SUCCESS

    @staticmethod
    def log_failures(cards: list[Card], status: list[Status]) -> None:
        success_count = sum(s is Status.SUCCESS for s in status)
        fail_count = sum(s is Status.FAIL for s in status)

        print(f'Succesfully downloaded {success_count}/{len(cards)} images.') # TODO: Proper logger
        print(f'Failed to download {fail_count}/{len(cards)} images.') # TODO: Proper logger

        if fail_count:
            print(f'Failed to download: ')
            for index, (card, status) in enumerate(zip(cards, status)):
                if status == Status.FAIL:
                    print(f'\tIndex: {index} | Name: {card.name}')

    @classmethod
    def fetch_cards(cls, cards: list[Card], output_dir: str | os.PathLike) -> None:
        output_dir = Path(output_dir)

        status = []
        fetcher = cls()

        for card in cards:
            status.append(fetcher.fetch_card(card, output_dir))

        cls.log_failures(cards, status)

    @classmethod
    def fetch_cards_parallel(cls, cards: list[Card], output_dir: str | os.PathLike, max_workers: int | None = None) -> None:

        output_dir = Path(output_dir)
        fetcher = cls()
        results: list[Status] = [Status.FAIL] * len(cards)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {executor.submit(fetcher.fetch_card, card, output_dir): i 
            for i, card in enumerate(cards)
        }

        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            try:
                results[i] = future.result()
            except Exception:
                traceback.print_exc()
                results[i] = Status.FAIL

        cls.log_failures(cards, results)


class MPCFillParser:
    @staticmethod
    def parse(deck_text: str) -> list[Card]:
        root = ET.fromstring(deck_text)
        fronts = root.find("fronts")
        if fronts is None:
            raise ValueError("No fronts found in decklist")

        cards_data = {}
        for front in fronts.findall("card"):
            slots = front.find("slots").text.split(",")
            cards_data[slots[0]] = {
                'name': front.find("name").text.split(".")[:-1][0],
                'id_front': front.find("id").text,
                'quantity': len(slots),
            }

        backs = root.find("backs") or []
        for back in backs:
            slot = back.find("slots").text.split(",")[0]
            cards_data[slot].update({'id_back': back.find('id').text})

        cards = []
        for index, card_data in enumerate(cards_data.values(), start=1):
            card = Card(
                card_data['name'],
                index,
                card_data['id_front'],
                id_back=card_data.get('id_back'),
                quantity=card_data['quantity']
            )
            cards.append(card)
        return cards
