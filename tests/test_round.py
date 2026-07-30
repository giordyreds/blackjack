from collections.abc import Callable

from blackjack.card import Card, Rank, Suit
from blackjack.hand import Hand
from blackjack.round import Action, Outcome, Round


class StubShoe:
    """Deals a predetermined sequence of cards, in order."""

    def __init__(self, cards: list[Card]) -> None:
        self._cards = list(cards)

    def deal(self) -> Card:
        return self._cards.pop(0)


def scripted(*actions: Action) -> Callable[[Hand], Action]:
    remaining = list(actions)

    def decide(hand: Hand) -> Action:
        return remaining.pop(0)

    return decide


def test_deal_initial_gives_two_cards_each_in_deal_order():
    shoe = StubShoe(
        [
            Card(Rank.TWO, Suit.SPADES),
            Card(Rank.THREE, Suit.HEARTS),
            Card(Rank.FOUR, Suit.CLUBS),
            Card(Rank.FIVE, Suit.DIAMONDS),
        ]
    )
    round_ = Round(shoe)
    round_.deal_initial()

    assert round_.player_hand.cards == [
        Card(Rank.TWO, Suit.SPADES),
        Card(Rank.FOUR, Suit.CLUBS),
    ]
    assert round_.dealer_hand.cards == [
        Card(Rank.THREE, Suit.HEARTS),
        Card(Rank.FIVE, Suit.DIAMONDS),
    ]


def test_player_can_hit_repeatedly_until_standing():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TWO, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)])
    round_.shoe = StubShoe([Card(Rank.THREE, Suit.CLUBS), Card(Rank.FOUR, Suit.DIAMONDS)])

    round_.play_player_turn(scripted(Action.HIT, Action.HIT, Action.STAND))

    assert round_.player_hand.value() == 11
    assert round_.player_hand.cards[-2:] == [
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.FOUR, Suit.DIAMONDS),
    ]


def test_player_stands_immediately_without_hitting():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])

    round_.play_player_turn(scripted(Action.STAND))

    assert round_.player_hand.value() == 17


def test_player_turn_stops_once_bust_even_if_told_to_hit_again():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    round_.shoe = StubShoe([Card(Rank.NINE, Suit.CLUBS)])

    decide = scripted(Action.HIT, Action.HIT)
    round_.play_player_turn(decide)

    assert round_.player_hand.is_bust is True
    assert round_.player_hand.value() == 26


def test_player_turn_is_skipped_on_a_natural():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])

    def decide(hand: Hand) -> Action:
        raise AssertionError("player should not be asked to act on a natural")

    round_.play_player_turn(decide)

    assert round_.player_hand.cards == [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
    ]


def test_dealer_hits_until_reaching_seventeen():
    round_ = Round(StubShoe([]))
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.TWO, Suit.HEARTS)])
    round_.shoe = StubShoe([Card(Rank.THREE, Suit.CLUBS), Card(Rank.FOUR, Suit.DIAMONDS)])

    round_.play_dealer_turn()

    assert round_.dealer_hand.value() == 19
    assert len(round_.dealer_hand.cards) == 4


def test_dealer_stands_on_hard_seventeen():
    round_ = Round(StubShoe([]))
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])

    round_.play_dealer_turn()

    assert round_.dealer_hand.cards == [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.SEVEN, Suit.HEARTS),
    ]


def test_dealer_stands_on_soft_seventeen():
    round_ = Round(StubShoe([]))
    round_.dealer_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.SIX, Suit.HEARTS)])

    round_.play_dealer_turn()

    assert round_.dealer_hand.value() == 17
    assert round_.dealer_hand.cards == [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.SIX, Suit.HEARTS),
    ]


def test_dealer_does_not_play_when_the_player_has_already_busted():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand(
        [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.CLUBS),
        ]
    )
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.FOUR, Suit.HEARTS)])
    round_.shoe = StubShoe([Card(Rank.TWO, Suit.CLUBS)])

    round_.play_dealer_turn()

    assert round_.dealer_hand.value() == 14


def test_resolve_player_bust_loses_regardless_of_dealer():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand(
        [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.CLUBS),
        ]
    )
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.NINE, Suit.CLUBS)])

    assert round_.resolve() is Outcome.PLAYER_BUST


def test_resolve_dealer_bust_when_player_has_not_busted():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS)])
    round_.dealer_hand = Hand(
        [
            Card(Rank.TEN, Suit.DIAMONDS),
            Card(Rank.NINE, Suit.CLUBS),
            Card(Rank.FIVE, Suit.SPADES),
        ]
    )

    assert round_.resolve() is Outcome.DEALER_BUST


def test_resolve_player_natural_beats_dealer_regular_twenty_one():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])
    round_.dealer_hand = Hand(
        [
            Card(Rank.SEVEN, Suit.DIAMONDS),
            Card(Rank.SEVEN, Suit.CLUBS),
            Card(Rank.SEVEN, Suit.SPADES),
        ]
    )

    assert round_.resolve() is Outcome.PLAYER_NATURAL


def test_resolve_both_naturals_is_a_push():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])
    round_.dealer_hand = Hand([Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS)])

    assert round_.resolve() is Outcome.PUSH


def test_resolve_dealer_natural_beats_player_regular_twenty_one():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand(
        [
            Card(Rank.SEVEN, Suit.SPADES),
            Card(Rank.SEVEN, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.CLUBS),
        ]
    )
    round_.dealer_hand = Hand([Card(Rank.ACE, Suit.DIAMONDS), Card(Rank.QUEEN, Suit.CLUBS)])

    assert round_.resolve() is Outcome.DEALER_WIN


def test_resolve_higher_total_wins():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS)])
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.SEVEN, Suit.CLUBS)])

    assert round_.resolve() is Outcome.PLAYER_WIN


def test_resolve_lower_total_loses():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.NINE, Suit.CLUBS)])

    assert round_.resolve() is Outcome.DEALER_WIN


def test_resolve_equal_totals_is_a_push():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)])
    round_.dealer_hand = Hand([Card(Rank.TEN, Suit.DIAMONDS), Card(Rank.EIGHT, Suit.CLUBS)])

    assert round_.resolve() is Outcome.PUSH


def test_play_runs_a_full_round_end_to_end():
    shoe = StubShoe(
        [
            Card(Rank.TEN, Suit.SPADES),  # player
            Card(Rank.TEN, Suit.HEARTS),  # dealer
            Card(Rank.SIX, Suit.CLUBS),  # player
            Card(Rank.SIX, Suit.DIAMONDS),  # dealer
            Card(Rank.TWO, Suit.SPADES),  # dealer hits to 18
        ]
    )
    round_ = Round(shoe)

    outcome = round_.play(scripted(Action.STAND))

    assert round_.player_hand.value() == 16
    assert round_.dealer_hand.value() == 18
    assert outcome is Outcome.DEALER_WIN
