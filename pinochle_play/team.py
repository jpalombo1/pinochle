from __future__ import annotations

from dataclasses import dataclass

from pinochle_play.player import Player


@dataclass
class Team:
    """Pinochle team.

    Attributes
    ----------
    team_num: (int) Team number
    """

    team_num: int

    def __post_init__(self) -> None:
        """

        Attributes
        ----------
        players: (list[Player]) List of all players in game.
        team_bid (int) Highest bid of team.
        round_score: (int) Score for both players on team in round.
        total_score (int) Total score of team.
        """
        self.players: list[Player] = []
        self.team_bid: int = 0
        self.round_score: int = 0
        self.total_score: int = 0

    def add_player(self, player: Player) -> None:
        """Add player to team."""
        self.players.append(player)

    def adjust_total_score(self):
        """Modify total score based on making bid and round score.

        If miss bid, lose points from total score. Reset round score to 0.
        """
        if self.round_score < self.team_bid:
            self.total_score -= self.team_bid
        else:
            self.total_score += self.round_score
        self.round_score = 0

    def add_score(self, score: int) -> None:
        """Add to round score based on both players meld, tricks won in round"""
        self.round_score += score

    def on_team(self, player: Player) -> bool:
        """Check if given player on team."""
        return player in self.players

    def set_bid(self, bid: int) -> None:
        """Set team bid needed to beat for trump team."""
        self.team_bid = bid

    def reset_round(self) -> None:
        """At end of round reset team bid and round score."""
        self.team_bid = 0
        self.round_score = 0

    def __str__(self) -> str:
        """String repr of team."""
        return f"Team {self.team_num} with {self.players}"

    def __repr__(self) -> str:
        """String repr of team."""
        return self.__str__()
