from __future__ import annotations

from dataclasses import dataclass

from pinochle_play.common import VALUE_MAP, Suits, Values


@dataclass
class Card:
    """Card with suit and value.

    Attributes
    ----------
    suit (Suits): Suit of card.
    value (Values): Value of card.
    """

    suit: Suits
    value: Values

    def __str__(self) -> str:
        """Return card value by _ of _ ."""
        return f"{self.value.value}{self.suit.value}"

    def __repr__(self) -> str:
        """Return card value by _ of _ ."""
        return self.__str__()

    def __eq__(self, other) -> bool:
        """Check if 2 cards equal if suit the same and value the same. Defer if no suit or value given."""
        return (self.suit == other.suit or other.suit == Suits.NONE) and (
            self.value == other.value or other.value == Values.NONE
        )

    def __lt__(self, other) -> bool:
        """Check which is smaller by value map index."""
        return VALUE_MAP[self.value] < VALUE_MAP[other.value]

    def __gt__(self, other) -> bool:
        """Check which is larger by value map index."""
        return VALUE_MAP[self.value] > VALUE_MAP[other.value]
