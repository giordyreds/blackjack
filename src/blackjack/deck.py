from blackjack.card import Card, Rank, Suit


class Deck:
    """A standard 52 unique-card set."""

    def __init__(self) -> None:
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]
