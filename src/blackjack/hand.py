from collections.abc import Iterable

from blackjack.card import Card, Rank


class Hand:
    """The cards held by the player or dealer during a round."""

    def __init__(self, cards: Iterable[Card] | None = None) -> None:
        self.cards = list(cards) if cards is not None else []
        self.is_split_aces = False
        self.is_doubled = False
        self.from_split = False

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def value(self) -> int:
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank is Rank.ACE)

        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    @property
    def is_bust(self) -> bool:
        return self.value() > 21

    @property
    def is_natural(self) -> bool:
        if self.is_split_aces:
            return False
        return len(self.cards) == 2 and self.value() == 21

    @property
    def is_pair(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].rank is self.cards[1].rank
