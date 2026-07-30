import random

from blackjack.card import Card
from blackjack.deck import Deck


class Shoe:
    """The dealing device holding several shuffled decks, reshuffled once a
    cut card near the configured penetration is reached."""

    NUM_DECKS = 6
    DEFAULT_PENETRATION = 0.75

    def __init__(
        self,
        rng: random.Random | None = None,
        penetration: float = DEFAULT_PENETRATION,
    ) -> None:
        self._rng = rng if rng is not None else random.Random()
        self._penetration = penetration
        self._reshuffle()

    @property
    def cards_remaining(self) -> int:
        return len(self._cards)

    def deal(self) -> Card:
        if self._dealt >= self._cut_card_position:
            self._reshuffle()

        self._dealt += 1
        return self._cards.pop()

    def _reshuffle(self) -> None:
        cards = [card for _ in range(self.NUM_DECKS) for card in Deck().cards]
        self._rng.shuffle(cards)

        self._cards = cards
        self._cut_card_position = round(len(cards) * self._penetration)
        self._dealt = 0
