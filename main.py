import logging
import random
import sys

# logging.basicConfig(filename="logging.log", level=logging.DEBUG, filemode="w+")
logging.basicConfig(
    format="%(asctime)s [%(filename)s:%(lineno)d] %(message)s",
    stream=sys.stdout,
    level=logging.INFO,
    filemode="w+",
)


class Player:
    """Player."""

    def __init__(self, player_name: str, computer: bool = True):
        self.player_name: str = player_name
        self.hand: list[Card] = []
        self.player_bid: int = 0
        self.use_card: Card = Card("", "")
        self.computer: bool = computer

    def __eq__(self, other) -> bool:
        return self.player_name == other.player_name

    def add_card(self, card: Card):
        """When dealt card, add it to hand."""
        self.hand.append(card)
        self.hand.sort(key=lambda c: c.suit)
        sorted(self.hand, reverse=True)

    def remove_card(self, use_card: Card):
        """Remove card from hand after playing it."""
        card_index = self.hand.index(use_card)
        self.hand.pop(card_index)

    def bid(self, bids_sofar: list[int]) -> int:
        if self.computer:
            return self.calculate_bid(bids_sofar)
        else:
            return self.manual_bid(bids_sofar)

    def manual_bid(self, bids_sofar: list[int]) -> int:
        while True:
            try:
                bid = int(
                    input(
                        f"Player: {self.player_name}\nEnter bid based on hand:\n{self.hand}\nHand score: {self.score_hand(show_melds=False)}\nPrevious bids: {bids_sofar}.\nEnter 20 or more to open: "
                    )
                )
                if not isinstance(bid, int):
                    raise ValueError("Please enter a valid number for bid.")
                break
            except ValueError:
                logging.info("Invalid bid, try again")
        return bid

    def calculate_bid(self, bids_sofar: list[int]) -> int:
        """Return player's point bid based on hand melds and partner bid. 0 is pass"""
        hand_score = self.score_hand(show_melds=False)
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

    def call_trump(self) -> str:
        """Return player's preffered trump suit based on hand."""
        counts = [self.hand.count(Card(suit, "")) for suit in suits]
        return suits[counts.index(max(counts))]

    def score_hand(self, trump_suit: str = "N/A", show_melds: bool = True) -> int:
        """Find out score of players hand based on melds, marraiges, runs, pinochle."""
        hand_score = 0
        # Pinochle gives score of 4
        if Card("♦", "J") in self.hand and Card("♠", "Q") in self.hand:
            hand_score += 4
            if show_melds:
                logging.info("pinochle 4")

        # Meld 9 of trump suit if known
        meld_count = self.hand.count(Card(trump_suit, "9"))
        if meld_count > 0:
            hand_score += meld_count
            if show_melds:
                logging.info(f"meld {meld_count}")

        for suit in suits:
            # Marraiges give 2
            if Card(suit, "K") in self.hand and Card(suit, "Q") in self.hand:
                hand_score += 2
                if show_melds:
                    logging.info(f"marraige {suit} 2")
                # Trump marraiges give 4
                if suit == trump_suit:
                    if show_melds:
                        logging.info(f"same marraige trump {suit} 2")
                    hand_score += 2
            # Runs give 15
            if (
                Card(suit, "A") in self.hand
                and Card(suit, "10") in self.hand
                and Card(suit, "K") in self.hand
                and Card(suit, "Q") in self.hand
                and Card(suit, "J") in self.hand
            ):
                logging.info(f"Run {suit} 15")
                hand_score += 15

        four_kind_values = [10, 8, 6, 4]
        for idx, value in enumerate(["A", "K", "Q", "J"]):
            # 4 of a kind
            if (
                Card(suits[0], value) in self.hand
                and Card(suits[1], value) in self.hand
                and Card(suits[2], value) in self.hand
                and Card(suits[3], value) in self.hand
            ):
                hand_score += four_kind_values[idx]
                if show_melds:
                    logging.info(f"four of a kind {value} {four_kind_values[idx]}")
        logging.debug(f"Player {self.player_name} hand {self.hand} score {hand_score}")
        if show_melds:
            logging.info(f"Player {self.player_name} score {hand_score}")
        # TODO Add seen cards for melds to pool of used cards for players to keep track of
        return hand_score

    def play_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: str
    ) -> Card:
        """Computer or user plays card."""
        use_card = Card("", "")
        if self.computer:
            use_card = self.calculate_card(trick, used_cards, trump_suit)
        else:
            use_card = self.manual_card(trick, used_cards, trump_suit)

        self.remove_card(use_card)
        logging.info(
            f"{self.player_name} play card {use_card} with trick cards {trick}"
        )
        logging.debug(f"{self.player_name} hand now  {self.hand} size {len(self.hand)}")
        return use_card

    def manual_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: str
    ) -> Card:
        """Make player choose the card to play. Make sure selection input is valid."""
        while True:
            try:
                card_index = (
                    int(
                        input(
                            f"Player: {self.player_name}\nTrump suit: {trump_suit} \nCurrent trick is {trick} \nUsed Cards: {used_cards}\nChoose card to use by number:\n{', '.join([f'{idx+1}.{card}'for idx,card in enumerate(self.hand)])} "
                        )
                    )
                    - 1
                )
                if not isinstance(card_index, int):
                    raise ValueError("Please enter a valid number for card to choose.")
                if card_index < 0 or card_index > len(self.hand) - 1:
                    raise ValueError("Please enter a number in range within your hand.")
                if not self.allowed_move(
                    trick, self.hand, self.hand[card_index], trump_suit
                ):
                    raise ValueError(
                        "Move is not allowed in this trick, please move again."
                    )
                break
            except ValueError:
                logging.info("Invalid card choice, try again")
        return self.hand[card_index]

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
        if not self.computer:
            logging.info(
                f"Playing card with {card.suit} even though hand has {num_trick_suit} cards of {trick_suit} and {num_trump_suit} cards of {trump_suit}. Illegal!"
            )
        return False

    def calculate_card(
        self, trick: list[Card], used_cards: list[Card], trump_suit: str
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
            use_card = self.best_leadoff_move(trump_suit)

        if not use_card == Card("", ""):
            if random.randint(1, 2) > 1:
                use_card = self.counter_move(trick_suit)
            else:
                use_card = self.discard_move(trick_suit)

        if use_card == Card("", ""):
            while True:
                use_card = random.choice(self.hand)
                if self.allowed_move(trick, self.hand, use_card, trump_suit):
                    break

        return use_card

    def best_leadoff_move(self, trump_suit: str) -> Card:
        """Pick best move when leading off. High trump cards, then bare aces, lower trump, lower cards."""
        return Card("", "")

    def force_move(self, trick_suit: str, trump_suit: str) -> Card:
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

        return Card("", "")

    def counter_move(self, trick_suit: str) -> Card:
        """Counter move depending on hand and trick. Play coutner to give your team points when teammate leads trick."""
        counter_card = Card("", "A")
        use_counter = False
        for card in self.hand:
            if card.suit == trick_suit and card > Card("", "Q") and card < counter_card:
                counter_card = card
                use_counter = True
                logging.debug(
                    f"Use card {counter_card} for best counter in hand {self.hand} with trick {trick_suit}."
                )

        if use_counter:
            return counter_card

        return Card("", "")

    def discard_move(self, trick_suit: str) -> Card:
        """Discard move when opposing team leading the trick. Dispose the least usable card you can."""
        discard_card = Card("", "A")
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

        return Card("", "")

    def reset_round(self):
        self.hand = []
        self.player_bid = 0

    def __str__(self) -> str:
        return f"Player {self.player_name} with hand {self.hand} size {len(self.hand)}."

    def __repr__(self) -> str:
        return f"Player {self.player_name} with hand {self.hand} size {len(self.hand)}."


class Team:
    """Pinochle team."""

    def __init__(self, team_num: int):
        self.players: list[Player] = []
        self.team_num: int = team_num
        self.team_bid: int = 0
        self.round_score: int = 0
        self.total_score: int = 0

    def add_player(self, player: Player):
        self.players.append(player)

    def adjust_total_score(self):
        """Modify total score based on making bid and round score."""
        if self.round_score < self.team_bid:
            self.total_score -= self.team_bid
            if self.total_score < 0:
                self.total_score = 0
        else:
            self.total_score += self.round_score
        self.round_score = 0

    def add_score(self, score: int):
        """Add to round score based on both players meld, tricks won in round"""
        self.round_score += score

    def on_team(self, player: Player) -> bool:
        """Check if given player on team."""
        return player in self.players

    def set_bid(self, bid: int):
        """Set team bid needed to beat for trump team."""
        self.team_bid = bid

    def reset_round(self):
        self.team_bid = 0
        self.round_score = 0

    def __str__(self) -> str:
        return f"Team {self.team_num} with {self.players}"

    def __repr__(self) -> str:
        return f"Team {self.team_num} with {self.players}"


class Game:
    """Game object."""

    def __init__(self):
        self.teams: list[Team] = []
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.round_num: int = 0
        self.trump_player: int = 0
        self.trump_suit: str = "N/A"
        self.meet_bid: int = 0
        self.max_score: int = 0
        self.used_cards: list[Card] = []

    def add_team(self, team: Team):
        self.players = []
        self.teams.append(team)
        # Add players 1 player per team at a time, keep adding until all players on team
        for player_num in range(len(team.players)):
            for team_num in range(len(self.teams)):
                self.players.append(self.teams[team_num].players[player_num])
        logging.info(f"All players {self.players}")

    def play_round(self):
        """Execute full round of pinochle."""
        self.shuffle_cards()
        self.deal_cards()
        self.bid_round()
        self.score_hands()
        self.tricks()
        self.cleanup_round()

    def shuffle_cards(self):
        """Shuffle pinochle deck."""
        self.deck = [
            Card(suit, value) for value in values for suit in suits for i in range(2)
        ]
        random.shuffle(self.deck)

    def deal_cards(self):
        """Deal deck evenly to players. Players add cards to hand."""
        for idx, card in enumerate(self.deck):
            player = self.players[idx % len(self.players)]
            player.add_card(card)
        logging.debug(f"Players {self.players}")

    def bid_round(self):
        """Players submit bids based on hands. Highest bid calls trump."""
        dealer = self.round_num % len(self.players)
        bids_sofar = []
        self.trump_player = len(self.players) - 1
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

    def score_hands(self):
        """Score meld hands and set team meet bid"""
        for player in self.players:
            for team in self.teams:
                if team.on_team(player):
                    score = player.score_hand(trump_suit=self.trump_suit)
                    team.add_score(score)
        for team in self.teams:
            logging.info(f"Team {team.team_num} Score {team.round_score} after meld")
            if team.on_team(self.players[self.trump_player]):
                team.set_bid(self.meet_bid)

    def tricks(self):
        """Play tricks."""
        player_go: int = self.trump_player
        for trick in range(12):
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

    def beat_card(self, best: Card, current: Card, trump: str) -> bool:
        """Determines winning card based on trump, value of cards.
        Current card only wins if trump while best isnt or if suits same/trump and current card value higher"""
        if not best == Card(trump, "") and current == Card(trump, ""):
            return True
        if best.suit == current.suit and best < current:
            return True
        return False

    def score_tricks(self, player: int, trick: list[Card]):
        """Score tricks for each team. Adjust final score based on making the bid."""
        point_values = ["A", "10", "K"]
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

    def cleanup_round(self):
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
        self.trump_suit = "N/A"
        self.meet_bid = 0
        self.used_cards = []

    def play(self, games: int = 1):
        for game in range(games):
            logging.debug(f"{self.players}")
            logging.debug(f"{self.teams}")
            while self.max_score < 120:
                self.play_round()


def main():
    team1 = Team(1)
    p1 = Player("Joe", computer=False)
    p2 = Player("Katie", computer=False)
    team1.add_player(p1)
    team1.add_player(p2)
    team2 = Team(2)
    p3 = Player("George")
    p4 = Player("Sue")
    team2.add_player(p3)
    team2.add_player(p4)
    game = Game()
    game.add_team(team1)
    game.add_team(team2)
    game.play()


if __name__ == "__main__":
    main()


def main():
    team1 = Team(1)
    p1 = Player("Joe", computer=False)
    p2 = Player("Katie", computer=False)
    team1.add_player(p1)
    team1.add_player(p2)
    team2 = Team(2)
    p3 = Player("George")
    p4 = Player("Sue")
    team2.add_player(p3)
    team2.add_player(p4)
    game = Game()
    game.add_team(team1)
    game.add_team(team2)
    game.play()


if __name__ == "__main__":
    main()
