from collections.abc import Callable

import pytest

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


def test_split_creates_two_independent_hands_from_a_pair():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.EIGHT, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)])
    round_.shoe = StubShoe(
        [
            Card(Rank.THREE, Suit.CLUBS),  # dealt to first split hand
            Card(Rank.FOUR, Suit.DIAMONDS),  # dealt to second split hand
        ]
    )

    round_.play_player_turn(scripted(Action.SPLIT, Action.STAND, Action.STAND))

    assert len(round_.player_hands) == 2
    first, second = round_.player_hands
    assert first.cards == [Card(Rank.EIGHT, Suit.SPADES), Card(Rank.THREE, Suit.CLUBS)]
    assert second.cards == [Card(Rank.EIGHT, Suit.HEARTS), Card(Rank.FOUR, Suit.DIAMONDS)]
    assert first.from_split is True
    assert second.from_split is True


def test_each_split_hand_is_played_out_independently_in_turn():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.NINE, Suit.SPADES), Card(Rank.NINE, Suit.HEARTS)])
    round_.shoe = StubShoe(
        [
            Card(Rank.TWO, Suit.CLUBS),  # dealt to first split hand
            Card(Rank.THREE, Suit.DIAMONDS),  # dealt to second split hand
            Card(Rank.FIVE, Suit.HEARTS),  # hit on first split hand
        ]
    )

    round_.play_player_turn(scripted(Action.SPLIT, Action.HIT, Action.STAND, Action.STAND))

    first, second = round_.player_hands
    assert first.cards == [
        Card(Rank.NINE, Suit.SPADES),
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.FIVE, Suit.HEARTS),
    ]
    assert second.cards == [Card(Rank.NINE, Suit.HEARTS), Card(Rank.THREE, Suit.DIAMONDS)]


def test_resplitting_is_allowed_up_to_three_total_hands():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.EIGHT, Suit.SPADES), Card(Rank.EIGHT, Suit.HEARTS)])
    round_.shoe = StubShoe(
        [
            Card(Rank.EIGHT, Suit.DIAMONDS),  # dealt to first split hand (itself a pair)
            Card(Rank.TWO, Suit.CLUBS),  # dealt to second split hand
            Card(Rank.FIVE, Suit.SPADES),  # dealt to first re-split hand
            Card(Rank.SIX, Suit.HEARTS),  # dealt to second re-split hand
        ]
    )

    round_.play_player_turn(
        scripted(Action.SPLIT, Action.SPLIT, Action.STAND, Action.STAND, Action.STAND)
    )

    assert len(round_.player_hands) == 3
    assert round_.player_hands[0].cards == [Card(Rank.EIGHT, Suit.SPADES), Card(Rank.FIVE, Suit.SPADES)]
    assert round_.player_hands[1].cards == [Card(Rank.EIGHT, Suit.DIAMONDS), Card(Rank.SIX, Suit.HEARTS)]
    assert round_.player_hands[2].cards == [Card(Rank.EIGHT, Suit.HEARTS), Card(Rank.TWO, Suit.CLUBS)]


def test_cannot_split_beyond_three_hands():
    round_ = Round(StubShoe([]))
    round_.player_hands = [
        Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS)]),
        Hand([Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SIX, Suit.DIAMONDS)]),
        Hand([Card(Rank.TWO, Suit.SPADES), Card(Rank.THREE, Suit.HEARTS)]),
    ]

    with pytest.raises(ValueError):
        round_.play_player_turn(scripted(Action.SPLIT))


def test_can_split_is_false_once_three_hands_are_in_play():
    round_ = Round(StubShoe([]))
    round_.player_hands = [
        Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.TEN, Suit.HEARTS)]),
        Hand([Card(Rank.FIVE, Suit.CLUBS), Card(Rank.SIX, Suit.DIAMONDS)]),
        Hand([Card(Rank.TWO, Suit.SPADES), Card(Rank.THREE, Suit.HEARTS)]),
    ]

    assert round_.can_split(round_.player_hands[0]) is False


def test_split_aces_receive_exactly_one_card_and_are_never_asked_to_act_again():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)])
    round_.shoe = StubShoe(
        [
            Card(Rank.KING, Suit.CLUBS),  # dealt to first split-aces hand
            Card(Rank.QUEEN, Suit.DIAMONDS),  # dealt to second split-aces hand
        ]
    )

    round_.play_player_turn(scripted(Action.SPLIT))

    first, second = round_.player_hands
    assert first.cards == [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.CLUBS)]
    assert second.cards == [Card(Rank.ACE, Suit.HEARTS), Card(Rank.QUEEN, Suit.DIAMONDS)]
    assert first.is_split_aces is True
    assert second.is_split_aces is True
    assert first.is_natural is False
    assert second.is_natural is False


def test_split_aces_hand_cannot_be_split_again():
    round_ = Round(StubShoe([]))
    ace_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)])
    ace_hand.is_split_aces = True
    round_.player_hands = [ace_hand]

    assert round_.can_split(ace_hand) is False


def test_double_down_doubles_the_bet_deals_one_card_and_stands():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.FIVE, Suit.SPADES), Card(Rank.SIX, Suit.HEARTS)])
    round_.shoe = StubShoe([Card(Rank.NINE, Suit.CLUBS)])

    round_.play_player_turn(scripted(Action.DOUBLE_DOWN))

    assert round_.player_hand.is_doubled is True
    assert round_.player_hand.cards == [
        Card(Rank.FIVE, Suit.SPADES),
        Card(Rank.SIX, Suit.HEARTS),
        Card(Rank.NINE, Suit.CLUBS),
    ]


def test_double_down_is_allowed_on_a_hand_that_came_from_a_split():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand([Card(Rank.SEVEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    round_.shoe = StubShoe(
        [
            Card(Rank.TWO, Suit.CLUBS),  # dealt to first split hand
            Card(Rank.THREE, Suit.DIAMONDS),  # dealt to second split hand
            Card(Rank.FOUR, Suit.SPADES),  # double-down card for first split hand
        ]
    )

    round_.play_player_turn(scripted(Action.SPLIT, Action.DOUBLE_DOWN, Action.STAND))

    first, second = round_.player_hands
    assert first.is_doubled is True
    assert first.cards == [
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.FOUR, Suit.SPADES),
    ]
    assert second.is_doubled is False
    assert second.cards == [Card(Rank.SEVEN, Suit.HEARTS), Card(Rank.THREE, Suit.DIAMONDS)]


def test_double_down_is_rejected_once_a_hand_has_more_than_two_cards():
    round_ = Round(StubShoe([]))
    round_.player_hand = Hand(
        [
            Card(Rank.TWO, Suit.SPADES),
            Card(Rank.THREE, Suit.HEARTS),
            Card(Rank.FOUR, Suit.CLUBS),
        ]
    )

    with pytest.raises(ValueError):
        round_.play_player_turn(scripted(Action.DOUBLE_DOWN))
