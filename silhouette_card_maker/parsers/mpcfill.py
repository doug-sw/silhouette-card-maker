from xml.etree import ElementTree as ET
from typing import Any, Dict, List
from silhouette_card_maker.models.faces import NormalizedCardFace, FaceType
from silhouette_card_maker.models.card import Card
from silhouette_card_maker.models.collections import CardCollection
from silhouette_card_maker.parsers.base import BaseParser

class MPCFillXMLParser(BaseParser):
    """
    Parse MPCFill XML into a CardCollection.
    """

    def parse(self, raw_data: str) -> CardCollection:
        """
        raw_data: MPCFill XML string
        """
        root = ET.fromstring(raw_data)
        collection = CardCollection()

        front_nodes = root.findall(".//fronts/card")
        back_nodes = root.findall(".//backs/card")

        fronts = [self._parse_face_node(node, FaceType.FRONT) for node in front_nodes]
        backs = [self._parse_face_node(node, FaceType.BACK) for node in back_nodes]

        slot_map: Dict[int, Card] = {}

        for face in fronts:
            for slot in face.data.slots:
                if slot not in slot_map:
                    slot_map[slot] = Card()
                slot_map[slot].add_face(face)

        for face in backs:
            for slot in face.data.slots:
                if slot not in slot_map:
                    slot_map[slot] = Card()
                slot_map[slot].add_face(face)

        for slot in sorted(slot_map.keys()):
            collection.add_card(slot_map[slot])

        return collection

    def _parse_face_node(self, node: ET.Element, face_type: FaceType) -> NormalizedCardFace:
        """
        Convert an XML <card> node into a NormalizedCardFace.
        """
        data = {
            "name": node.findtext("name"),
            "id": node.findtext("id"),
            "slots": [int(s.strip()) for s in node.findtext("slots").split(",")],
            "query": node.findtext("query"),
        }

        return NormalizedCardFace(face_type=face_type, data=data)
