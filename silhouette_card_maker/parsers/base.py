from abc import ABC, abstractmethod
from typing import List
from silhouette_card_maker.models.card import Card

class BaseParser(ABC):
    @abstractmethod
    def parse(self, deck_text: str) -> List[Card]:
        """
        Parse a deck representation (string) and return a list of Card objects.
        """
        pass
