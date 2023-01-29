from __future__ import annotations

import logging
import random

from pinochle_play.card import Card
from pinochle_play.common import Suits, Values
from pinochle_play.player import Player


class Computer(Player):
    """Computer player."""

    def bid(self, bids_sofar: list[int]) -> int:
        """Return player's point bid based on hand melds and partner bid. 0 is pass."""
        hand_score = self.score_hand()
        max_bid = max(bids_sofar) if len(bids_sofar) > 1 else 0
        partner_bid = 0
        if len(bids_sofar) > 1:
            partner_bid = bids_sofar[len(bids_sofar) - 2]
            logging.debug(f"bids so far {bids_sofar}")
        logging.debug(f"partner bid {partner_bid}")

        # TODO: Improve bidding based on real element and partner bid
        if hand_score < max_bid - 16:
            self.player_bid = 0
        if hand_score < 4:
            self.player_bid = 20
        elif hand_score < 10:
            self.player_bid = 21
        else:
            self.player_bid = 22
        return self.player_bid

    def call_trump(self) -> Suits:
        """Return player's preffered trump suit based on hand. Just returns suit with most cards in hand."""
        counts_map = {
            suit: self.hand.count(Card(suit, Values.NONE))
            for suit in Suits
            if suit != Suits.NONE
        }
        return max(counts_map, key=lambda suit: counts_map.get(suit, 0))

    def play_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: Suits
    ) -> Card:
        """Calculate the best card to play based on trick, used cards, aand trump."""
        use_card = self.calculate_card(trick, used_cards, trump_suit=trump_suit)
        self.remove_card(use_card)
        logging.info(
            f"{self.player_name} play card {use_card} with trick cards {trick}"
        )
        logging.debug(f"{self.player_name} hand now  {self.hand} size {len(self.hand)}")
        return use_card

    def calculate_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: Suits
    ) -> Card:
        """Computer choose card to play based on focing, strategy, partner, etc."""
        # TODO: determine best card using current trick, used_cards, partner card. Counter if partner winning, else put low, more startegy
        # partner_card = None
        trick_suit = trump_suit

        # if len(trick) > 1:
        #     partner_card = trick[len(trick) - 2]

        if len(trick) > 0:
            trick_suit = trick[0].suit
            use_card = self.force_move(trick_suit, trump_suit)
        else:
            use_card = self.best_leadoff_move()

        if not use_card == Card(Suits.NONE, Values.NONE):
            if random.randint(1, 2) > 1:
                use_card = self.counter_move(trick_suit)
            else:
                use_card = self.discard_move(trick_suit)

        if use_card == Card(Suits.NONE, Values.NONE):
            while True:
                use_card = random.choice(self.hand)
                if self.allowed_move(trick, self.hand, use_card, trump_suit):
                    break

        return use_card

    def best_leadoff_move(self) -> Card:
        """Pick best move when leading off. High trump cards, then bare aces, lower trump, lower cards."""
        # TODO: insert logic
        return Card(Suits.NONE, Values.NONE)

    def force_move(self, trick_suit: Suits, trump_suit: Suits) -> Card:
        """Force move depending on hand and trick. If one card of trick suit, must play. If one card of trump suit if none trick suit, must play."""
        trick_suit_cards = [card for card in self.hand if card.suit == trick_suit]
        if len(trick_suit_cards) == 1:
            logging.debug(
                f"Must play {trick_suit_cards[0]} since only card in hand {self.hand} of trick suit {trick_suit}."
            )
            return trick_suit_cards[0]

        trump_suit_cards = [card for card in self.hand if card.suit == trump_suit]
        if len(trump_suit_cards) == 1:
            logging.debug(
                f"Must play {trump_suit_cards[0]} since only card in hand {self.hand} of trump suit {trump_suit}."
            )
            return trump_suit_cards[0]

        return Card(Suits.NONE, Values.NONE)

    def counter_move(self, trick_suit: Suits) -> Card:
        """Counter move depending on hand and trick. Play counter to give your team points when teammate leads trick. Use least high counter, K before 10 before A"""
        counter_card = Card(Suits.NONE, Values.ACE)
        use_counter = False
        for card in self.hand:
            if (
                card.suit == trick_suit
                and card > Card(Suits.NONE, Values.QUEEN)
                and card < counter_card
            ):
                counter_card = card
                use_counter = True
                logging.debug(
                    f"Use card {counter_card} for best counter in hand {self.hand} with trick {trick_suit}."
                )

        if use_counter:
            return counter_card

        return Card(Suits.NONE, Values.NONE)

    def discard_move(self, trick_suit: Suits) -> Card:
        """Discard move when opposing team leading the trick. Dispose the least valued usable card you can."""
        discard_card = Card(Suits.NONE, Values.ACE)
        use_discard = False
        for card in self.hand:
            if card.suit == trick_suit and not card > discard_card:
                discard_card = card
                use_discard = True
                logging.debug(
                    f"Use card {discard_card} for best discard in hand {self.hand} with trick {trick_suit}."
                )

        if use_discard:
            return discard_card

        return Card(Suits.NONE, Values.NONE)
