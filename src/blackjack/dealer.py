from enum import Enum

from blackjack.card import Card, Rank
from blackjack.hand import Hand

_TEN_VALUE_RANKS = {Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING}


class PeekOutcome(Enum):
    """The immediate round result when the dealer's peek finds a Natural."""

    DEALER_WINS = "dealer_wins"
    PUSH = "push"


def dealer_should_peek(up_card: Card) -> bool:
    """Whether the dealer's up-card requires a peek at the Hole Card."""
    return up_card.rank is Rank.ACE or up_card.rank in _TEN_VALUE_RANKS


def dealer_peek(player_hand: Hand, dealer_hand: Hand) -> PeekOutcome | None:
    """Check the dealer's Hole Card for a Natural right after the initial deal.

    Assumes the dealer's up-card is dealer_hand.cards[0] and the face-down
    Hole Card is dealer_hand.cards[1]. Returns the outcome that ends the
    round immediately if the peek finds a dealer Natural, or None if the
    round should continue to player action.
    """
    up_card = dealer_hand.cards[0]
    if not dealer_should_peek(up_card) or not dealer_hand.is_natural:
        return None

    if player_hand.is_natural:
        return PeekOutcome.PUSH

    return PeekOutcome.DEALER_WINS
