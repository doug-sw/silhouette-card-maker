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


MPCFILL_REQUEST_URL = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="


class Status(enum.Enum):
    SUCCESS = enum.auto()
    FAIL = enum.auto()


class Card:
    def __init__(self, name: str, index: int, id_front: str, id_back: str | None = None, quantity: int = 1):
        self.name = name
        self.index = index
        self.id_front = id_front
        self.id_back = id_back
        self.quantity = quantity

    @staticmethod
    def _request(card_id: str) -> requests.Response:
        resp = requests.get(MPCFILL_REQUEST_URL + card_id, headers={"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"})
        resp.raise_for_status()
        return resp

    def download_image(self, card_id: str, output_dir: str | os.PathLike) -> Status:
        print(f'{self.index} download started.')
        resp = Card._request(card_id)
        print(f'{self.index} download completed.')
        if resp.content is None:
            return status.FAIL
        image = b64decode(resp.content)
        file_ext = guess_extension(image)
        card_name = remove_nonalphanumeric(self.name)
        for counter in range(1, self.quantity+1):
            image_filename = f'{self.index}{card_name}{counter}.{file_ext}'
            image_filepath = Path(output_dir) / image_filename
            with open(image_filepath, 'wb') as file:
                file.write(image)
        return Status.SUCCESS

    def fetch(self, output_dir: str | os.PathLike) -> Status:
        status = [Status.SUCCESS, Status.SUCCESS]
        status[0] = self.download_image(self.id_front, Path(output_dir) / "front")
        if self.id_back:
            status[1] = self.download_image(self.id_back, Path(output_dir) / "double_sided")
        return Status.FAIL if Status.FAIL in status else Status.SUCCESS


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
            slot = front.find("slots").text.split(",")[0]
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
        status = []
        for card in cards:
            status.append(card.fetch(output_dir))
        cls.log_failures(cards, status)

    @classmethod
    def fetch_cards_parallel(cls, cards: list[Card], output_dir: str | os.PathLike, max_workers: int | None = None) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_card = {executor.submit(card.fetch, output_dir): card for card in cards}

        status = {card: Status.FAIL for card in cards}
        for future in concurrent.futures.as_completed(future_to_card):
            card = future_to_card[future]
            try:
                status[card] = future.result()
            except:
                print(traceback.format_exc())
        cls.log_failures(status.keys(), status.values())



