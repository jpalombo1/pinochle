from __future__ import annotations

import logging
import random

from pinochle_play.card import Card
from pinochle_play.common import Suits, Values
from pinochle_play.player import Player
from pinochle_play.team import Team


class Game4Player:
    """Game object for 4 player, 2 on 2 pinochle.."""

    def __init__(self) -> None:
        """
        Attributes
        ----------
        teams (list[Team]): list of teams
        players (list[Player]): list of players
        deck (list[Card]): pinchle deck of cards
        round_num (int): Round number
        trump_player (int): player number of trump caller.
        trump_suit (Suits): trump suit in current round.
        meet_bid (int): Highest bid in current round.
        mmax_score (int): Score of team with highest score.
        used_card (list[Card]): Cards used by players.
        """
        self.teams: list[Team] = []
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.round_num: int = 0
        self.trump_player: int = 0
        self.trump_suit: Suits = Suits.NONE
        self.meet_bid: int = 0
        self.max_score: int = 0
        self.used_cards: list[Card] = []

    def add_team(self, team: Team) -> None:
        """Add team to game, including players. Add players 1 at a time per team so p1 = team1 p1, p2 = team 2 p1, p3 = team1 p2, etc."""
        self.players = []
        self.teams.append(team)
        # Add players 1 player per team at a time, keep adding until all players on team
        for player_num in range(len(team.players)):
            for team_num in range(len(self.teams)):
                self.players.append(self.teams[team_num].players[player_num])
        logging.info(f"All players {self.players}")

    def play_round(self) -> None:
        """Execute full round of pinochle."""
        self.shuffle_cards()
        self.deal_cards()
        self.bid_round()
        self.score_hands()
        self.tricks()
        self.cleanup_round()

    def shuffle_cards(self) -> None:
        """Construct pinochle deck 2 of each suit/value card excluding none, then shuffle deck."""
        self.deck = [
            Card(suit, value)
            for value in Values
            for suit in Suits
            for _ in range(2)
            if suit != Suits.NONE and value != Values.NONE
        ]
        random.shuffle(self.deck)

    def deal_cards(self) -> None:
        """Deal deck evenly to players. Players add cards to hand."""
        for idx, card in enumerate(self.deck):
            player = self.players[idx % len(self.players)]
            player.add_card(card)
        logging.debug(f"Players {self.players}")

    def bid_round(self) -> None:
        """Players submit bids based on hands. Highest bid calls trump, default is last player before dealer. Set bid to meet."""
        dealer = self.round_num % len(self.players)
        bids_sofar: list[int] = []
        self.trump_player = (dealer + len(self.players) - 1) % len(self.players)
        for idx in range(len(self.players)):
            player_go = (dealer + idx) % len(self.players)
            player_bid = self.players[player_go].bid(bids_sofar)
            if len(bids_sofar) == 0 or player_bid > max(bids_sofar):
                self.trump_player = player_go
                logging.info(
                    f"{self.players[player_go].player_name} bid {player_bid}, which is current highest."
                )
            bids_sofar.append(player_bid)
        self.trump_suit = self.players[self.trump_player].call_trump()
        logging.info(
            f"Trump suit: {self.trump_suit} called by {self.players[self.trump_player].player_name} with max bid {max(bids_sofar)}"
        )
        self.meet_bid = max(bids_sofar)

    def score_hands(self) -> None:
        """Score meld hands and set team meet bid for team which trump player is on."""
        for player in self.players:
            for team in self.teams:
                if team.on_team(player):
                    score = player.score_hand(trump_suit=self.trump_suit)
                    team.add_score(score)
        for team in self.teams:
            logging.info(f"Team {team.team_num} Score {team.round_score} after meld")
            if team.on_team(self.players[self.trump_player]):
                team.set_bid(self.meet_bid)

    def tricks(self) -> None:
        """Play tricks. Number of tricks given by cards / players, take turn starting with trump player then with each trick winner."""
        num_tricks = len(self.deck) // len(self.players)
        player_go: int = self.trump_player
        for _ in range(num_tricks):
            trick: list[Card] = []
            for idx in range(len(self.players)):
                turn = (player_go + idx) % len(self.players)
                trick.append(
                    self.players[turn].play_card(
                        trick, self.used_cards, self.trump_suit
                    )
                )
            player_go = self.trick_winner(trick, player_go)
            self.score_tricks(player_go, trick)
            self.used_cards += trick
            logging.debug(f"Used cards {self.used_cards} {len(self.used_cards)}")

    def trick_winner(self, trick: list[Card], player_offset: int) -> int:
        """Determine trick winner based on cards played."""
        winning_player = player_offset
        for idx, card in enumerate(trick):
            actual_player = (player_offset + idx) % len(self.players)
            if idx == 0:
                best_card = card
            else:
                will_beat = self.beat_card(best_card, card, self.trump_suit)
                if will_beat:
                    best_card = card
                    winning_player = actual_player
        return winning_player

    def beat_card(self, best: Card, current: Card, trump: Suits) -> bool:
        """Determines winning card based on trump, value of cards.
        Current card only wins if trump while best isnt or if suits same/trump and current card value higher"""
        if not best == Card(trump, Values.NONE) and current == Card(trump, Values.NONE):
            return True
        if best.suit == current.suit and best < current:
            return True
        return False

    def score_tricks(self, player: int, trick: list[Card]) -> None:
        """Score tricks for each team. Adjust final score based on making the bid."""
        point_values = [Values.ACE, Values.TEN, Values.KING]
        trick_points = 0
        for card in trick:
            if card.value in point_values:
                trick_points += 1
        winning_player = self.players[player]
        logging.info(
            f"{trick} won by {winning_player.player_name} for {trick_points} points"
        )
        for team in self.teams:
            if team.on_team(winning_player):
                team.add_score(trick_points)
                logging.info(
                    f"Team {team.team_num} Score {team.round_score} , gained {trick_points} trick points"
                )

    def cleanup_round(self) -> None:
        """Reset roubd for players and teams."""
        for player in self.players:
            player.reset_round()
        self.round_num += 1
        for team in self.teams:
            team.adjust_total_score()
            logging.info(f"Total score {team.players} {team.total_score}")
            team.reset_round()
        scores = [team.total_score for team in self.teams]
        self.max_score = max(scores)
        logging.info(
            f"Round {self.round_num} Max score {self.max_score} by {self.teams[scores.index(self.max_score)].players}"
        )
        self.trump_player = 0
        self.trump_suit = Suits.NONE
        self.meet_bid = 0
        self.used_cards = []

    def play(self, games: int = 1, max_score: int = 120) -> None:
        """Overall play method to keep playing rounds until max score reached for given number of games."""
        for _ in range(games):
            logging.debug(f"{self.players}")
            logging.debug(f"{self.teams}")
            while self.max_score < max_score:
                self.play_round()
