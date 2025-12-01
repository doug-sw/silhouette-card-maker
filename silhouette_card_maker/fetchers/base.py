from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from silhouette_card_maker.models import Card, CardSide, Status

class BaseCardImageFetcher(ABC):
    """Abstract base class for card image fetchers."""

    @abstractmethod
    def fetch_card(self, card: Card, output_dir: Path) -> Status:
        """Fetch all images for a single card."""
        pass

    @abstractmethod
    def download_image(self, card: Card, side: CardSide, output_dir: Path) -> Status:
        """Download a specific side image for a card."""
        pass

    @classmethod
    def fetch_cards(cls, cards: List[Card], output_dir: Path) -> None:
        """Fetch multiple cards serially."""
        fetcher = cls()
        for card in cards:
            fetcher.fetch_card(card, output_dir)

    @classmethod
    def fetch_cards_parallel(cls, cards: List[Card], output_dir: Path, max_workers: int | None = None) -> None:
        """
        Optional: Fetch multiple cards in parallel.
        By default, falls back to serial fetching if parallelization is not supported.
        Concrete implementations can override this.
        """
        print("Parallel fetching not supported; falling back to serial fetching.")
        cls.fetch_cards(cards, output_dir)