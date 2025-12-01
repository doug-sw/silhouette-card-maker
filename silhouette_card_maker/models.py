from dataclasses import dataclass
from typing import Optional
import enum

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
