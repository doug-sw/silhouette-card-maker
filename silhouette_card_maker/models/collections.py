from dataclasses import dataclass, field
from typing import List, Iterator
from silhouette_card_maker.models.card import Card

@dataclass
class CardCollection:
    """
    Container for multiple Card objects.
    """
    cards: List[Card] = field(default_factory=list)

    def add_card(self, card: Card) -> None:
        """
        Add a card to the collection.
        Multiple cards with the same name are allowed.
        """
        self.cards.append(card)

    def __len__(self) -> int:
        return len(self.cards)

    def __iter__(self) -> Iterator[Card]:
        return iter(self.cards)

    def doublesided_cards(self) -> List[Card]:
        """
        Return a list of all cards that are doublesided.
        """
        return [card for card in self.cards if card.doublesided]
