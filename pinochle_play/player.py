from __future__ import annotations

import logging
from abc import ABC, abstractclassmethod
from dataclasses import dataclass

from pinochle_play.card import Card
from pinochle_play.common import Suits, Values


@dataclass
class Player(ABC):
    """Player class.

    Attributes
    ----------
    player_name (str): the player's name
    commputer (bool): Determine if hman or computer player.
    """

    player_name: str

    def __post_init__(self):
        """
        Define class attributes post init.

        Attributes
        ----------
        hand (list[Card]) : the player's current hand of cards.
        player_bid (int): The player's bid.
        use_card (Card): Current card to play, currently None card.
        """
        self.hand: list[Card] = []
        self.player_bid: int = 0
        self.use_card: Card = Card(Suits.NONE, Values.NONE)

    def __eq__(self, other) -> bool:
        """Determines if the same player."""
        return self.player_name == other.player_name

    def add_card(self, card: Card) -> None:
        """When dealt card, add it to hand, then sort hand by suit and value in suit."""
        self.hand.append(card)
        self.hand.sort(key=lambda c: c.suit.value)
        sorted(self.hand, reverse=True)

    def remove_card(self, use_card: Card) -> None:
        """Remove card from hand after playing it."""
        self.hand.pop(self.hand.index(use_card))

    @abstractclassmethod
    def bid(self, bids_sofar: list[int]) -> int:
        """Play bid method."""
        pass

    @abstractclassmethod
    def call_trump(self) -> Suits:
        """Return player's preffered trump suit based on hand."""
        pass

    @abstractclassmethod
    def play_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: str
    ) -> Card:
        """Computer or user plays card."""
        pass

    def score_hand(self, trump_suit: Suits = Suits.NONE) -> int:
        """Find out score of players hand based on melds, marraiges, runs, pinochle, 4kind."""
        # TODO Add seen cards for melds to pool of used cards for players to keep track of
        hand_score = self._score_pinochle()
        hand_score += self._score_meld(trump_suit)
        hand_score += self._score_marraiges(trump_suit)
        hand_score += self._score_runs()
        hand_score = self._score_4kind()
        return hand_score

    def _score_pinochle(self) -> int:
        """Pinochle gives score of 4."""
        if (
            Card(Suits.DIAMOND, Values.JACK) in self.hand
            and Card(Suits.CLUB, Values.QUEEN) in self.hand
        ):
            return 4
        return 0

    def _score_meld(self, trump_suit: Suits) -> int:
        """Score number of 9s in hand that match trump."""
        return self.hand.count(Card(trump_suit, Values.NINE))

    def _score_marraiges(self, trump_suit: Suits) -> int:
        """Check for marraige of each suit in hand. If"""
        marraige_score = 0
        for suit in Suits:
            if (
                Card(suit, Values.KING) in self.hand
                and Card(suit, Values.QUEEN) in self.hand
            ):
                if suit == Suits.NONE:
                    continue
                marraige_score += 4 if suit == trump_suit else 2
        return marraige_score

    def _score_runs(self) -> int:
        """Runs give 15."""
        run_score = 0
        for suit in Suits:
            if (
                Card(suit, Values.ACE) in self.hand
                and Card(suit, Values.TEN) in self.hand
                and Card(suit, Values.KING) in self.hand
                and Card(suit, Values.QUEEN) in self.hand
                and Card(suit, Values.JACK) in self.hand
            ):
                if suit == Suits.NONE:
                    continue
                run_score += 15
        return run_score

    def _score_4kind(self) -> int:
        """4 of a kind scoring."""
        kind_score = 0
        four_kind_values = {
            Values.ACE: 10,
            Values.KING: 8,
            Values.QUEEN: 6,
            Values.JACK: 4,
        }
        for value, point_value in four_kind_values.items():
            if (
                Card(Suits.CLUB, value) in self.hand
                and Card(Suits.DIAMOND, value) in self.hand
                and Card(Suits.HEART, value) in self.hand
                and Card(Suits.SPADE, value) in self.hand
            ):
                kind_score += point_value
        return kind_score

    def allowed_move(
        self, trick: list[Card], hand: list[Card], card: Card, trump_suit: str
    ) -> bool:
        """Determine if player is making legal move."""
        # TODO Make logic
        if card.suit == trump_suit:
            logging.debug("Player playing trump suit. Always legal.")
            return True
        if len(trick) == 0:
            logging.debug("Player playing first card, anything legal")
            return True
        trick_suit = trick[0].suit
        if card.suit == trick_suit:
            logging.debug("Player playing trick suit, normal and legal")
            return True
        num_trick_suit = len(
            [handcard for handcard in hand if handcard.suit == trick_suit]
        )
        num_trump_suit = len(
            [handcard for handcard in hand if handcard.suit == trump_suit]
        )
        if num_trick_suit == 0 and num_trump_suit == 0:
            logging.debug("No trump or trick suit to play, anything legal")
            return True
        logging.info(
            f"Playing card with {card.suit} even though hand has {num_trick_suit} cards of {trick_suit} and {num_trump_suit} cards of {trump_suit}. Illegal!"
        )
        return False

    def reset_round(self):
        """Reset hand and bid."""
        self.hand = []
        self.player_bid = 0

    def __str__(self) -> str:
        return f"Player {self.player_name} with hand {self.hand} size {len(self.hand)}."

    def __repr__(self) -> str:
        return f"Player {self.player_name} with hand {self.hand} size {len(self.hand)}."
