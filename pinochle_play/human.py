from __future__ import annotations

import logging

from pinochle_play.card import Card
from pinochle_play.common import Suits
from pinochle_play.player import Player


class Human(Player):
    """Human Player."""

    def bid(self, bids_sofar: list[int]) -> int:
        """Prompt for player to enter bid. If not integer, try again."""
        while True:
            try:
                bid = int(
                    input(
                        f"Player: {self.player_name}\n"
                        f"Enter bid based on hand:\n{self.hand}\n"
                        f"Hand score: {self.score_hand()}\n"
                        f"Previous bids: {bids_sofar}.\nEnter 20 or more to open: "
                    )
                )
                if not isinstance(bid, int):
                    raise ValueError("Please enter a valid number for bid.")
                break
            except ValueError:
                logging.info("Invalid bid! Try again!")
        return bid

    def call_trump(self) -> Suits:
        """Return player's preffered trump suit based on hand. Just returns suit with most cards in hand."""
        while True:
            try:
                suit = input(
                    f"Player: {self.player_name}\n"
                    f"Enter trump card based on hand:\n{self.hand}\n"
                    f"Hand score: {self.score_hand()}\n"
                    f"Choose from: {[suit.value for suit in Suits if suit != Suits.NONE]}: "
                )
                suit_map: dict[str, Suits] = {suit.value: suit for suit in Suits}
                suit_val = suit_map[suit]
                break
            except ValueError:
                logging.info("Suit invalid! Try again!")
        return suit_val

    def play_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: Suits
    ) -> Card:

        use_card = self.input_card(trick, used_cards, trump_suit=trump_suit)
        self.remove_card(use_card)
        logging.info(
            f"{self.player_name} play card {use_card} with trick cards {trick}"
        )
        logging.debug(f"{self.player_name} hand now  {self.hand} size {len(self.hand)}")
        return use_card

    def input_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: Suits
    ) -> Card:
        """Make player choose the card to play. Make sure selection input is valid."""
        allowed_card_idxs = self.allowed_cards(trick, self.hand, trump_suit)
        allowed_cards = [self.hand[card_idx] for card_idx in allowed_card_idxs]
        while True:
            try:
                card_index = int(
                    input(
                        f"Player: {self.player_name}\n"
                        f"Trump suit: {trump_suit} \n"
                        f"Current trick is {trick} \n"
                        f"Used Cards: {used_cards}\n"
                        f"Allowed Moves: {allowed_cards} Indexes: {allowed_card_idxs}\n"
                        f"Choose card to use by number:\n"
                        f"{', '.join([f'{idx}.{card}'for idx,card in enumerate(self.hand)])} "
                    )
                )
                if not isinstance(card_index, int):
                    raise ValueError("Please enter a valid number for card to choose.")
                if card_index not in range(0, len(self.hand)):
                    raise ValueError("Please enter a number in range within your hand.")
                if self.hand[card_index] not in allowed_cards:
                    raise ValueError(
                        "Move is not allowed in this trick, please move again."
                    )
                break
            except ValueError:
                logging.info("Invalid card choice, try again")
        return self.hand[card_index]

    def allowed_cards(
        self, trick: list[Card], hand: list[Card], trump_suit: Suits
    ) -> list[int]:
        """Get all card indexes allowed to be played."""
        return [
            card_idx
            for card_idx, card in enumerate(self.hand)
            if self.allowed_move(trick, hand, card, trump_suit)
        ]
