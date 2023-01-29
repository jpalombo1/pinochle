import logging
import sys

from pinochle_play.computer import Computer
from pinochle_play.game import Game4Player
from pinochle_play.human import Human
from pinochle_play.team import Team

# logging.basicConfig(filename="logging.log", level=logging.DEBUG, filemode="w+")
logging.basicConfig(
    format="%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    stream=sys.stdout,
    level=logging.INFO,
    filemode="w+",
)


def main():
    """Main method to add players, teams, and play game."""
    team1 = Team(1)
    p1 = Human("Joe")
    p2 = Computer("Katie")
    team1.add_player(p1)
    team1.add_player(p2)
    team2 = Team(2)
    p3 = Computer("George")
    p4 = Computer("Sue")
    team2.add_player(p3)
    team2.add_player(p4)
    game = Game4Player()
    game.add_team(team1)
    game.add_team(team2)
    game.play()


if __name__ == "__main__":
    main()
