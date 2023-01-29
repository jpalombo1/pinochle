from enum import Enum


class Suits(Enum):
    """Card suits."""

    HEART = "♥"
    SPADE = "♠"
    CLUB = "♣"
    DIAMOND = "♦"
    NONE = ""


class Values(Enum):
    """Card values in order of worst to best."""

    NINE = "9"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    TEN = "10"
    ACE = "A"
    NONE = ""


VALUE_MAP = {value: idx for idx, value in enumerate(Values)}
