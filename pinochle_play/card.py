from __future__ import annotations
from pinochle_play.common import Suits, Values, VALUE_MAP
from dataclasses import dataclass


@dataclass
class Card:
    "Card with suit and value."

    suit: Suits
    value: Values

    def __str__(self) -> str:
        """Return card value by _ of _ ."""
        return f"{self.value}{self.suit}"

    def __repr__(self) -> str:
        """Return card value by _ of _ ."""
        return self.__str__()

    def __eq__(self, other: Card) -> bool:
        """Check if 2 cards equal if suit the same and value the same.."""
        return self.suit == other.suit and self.value == other.value

    def __lt__(self, other: Card) -> bool:
        """Check which is smaller by value map index."""
        return VALUE_MAP[self.value] < VALUE_MAP[other.value]

    def __gt__(self, other: Card) -> bool:
        """Check which is larger by value map index."""
        return VALUE_MAP[self.value] > VALUE_MAP[other.value]
