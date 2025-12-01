

# silhouette_card_maker/parsers/mpcfill.py

from xml.etree import ElementTree as ET
from pathlib import Path
from typing import List
from silhouette_card_maker.models import Card
from silhouette_card_maker.parsers.base import BaseDeckParser

class MPCFillParser(BaseDeckParser):
    def parse(self, deck_text: str) -> List[Card]:
        root = ET.fromstring(deck_text)
        fronts = root.find("fronts")
        if fronts is None:
            raise ValueError("No fronts found in decklist")

        cards_data = {}
        for front in fronts.findall("card"):
            slots_text = front.find("slots").text or ""
            slots = slots_text.split(",")
            name_text = front.find("name").text or ""
            card_id = front.find("id").text or ""
            cards_data[slots[0]] = {
                "name": ".".join(name_text.split(".")[:-1]) if "." in name_text else name_text,
                "id_front": card_id,
                "quantity": len(slots),
            }

        backs = root.find("backs") or []
        for back in backs:
            slot_text = back.find("slots").text or ""
            slot = slot_text.split(",")[0] if slot_text else None
            if slot and slot in cards_data:
                card_back_id = back.find("id").text or None
                cards_data[slot]["id_back"] = card_back_id

        cards = []
        for index, card_data in enumerate(cards_data.values(), start=1):
            card = Card(
                name=card_data["name"],
                index=index,
                id_front=card_data["id_front"],
                id_back=card_data.get("id_back"),
                quantity=card_data["quantity"],
            )
            cards.append(card)

        return cards
