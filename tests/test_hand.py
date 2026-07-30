from blackjack.card import Card, Rank, Suit
from blackjack.hand import Hand


def test_hard_total_sums_face_values():
    hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    assert hand.value() == 17


def test_face_cards_are_worth_ten():
    hand = Hand([Card(Rank.KING, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS)])
    assert hand.value() == 20


def test_soft_total_counts_ace_as_eleven_when_it_does_not_bust():
    hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.SIX, Suit.HEARTS)])
    assert hand.value() == 17


def test_ace_counts_as_one_when_eleven_would_bust():
    hand = Hand(
        [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.SIX, Suit.HEARTS),
            Card(Rank.NINE, Suit.CLUBS),
        ]
    )
    assert hand.value() == 16


def test_multiple_aces_only_one_counts_as_eleven():
    hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)])
    assert hand.value() == 12


def test_multiple_aces_reduce_as_needed_to_avoid_bust():
    hand = Hand(
        [
            Card(Rank.ACE, Suit.SPADES),
            Card(Rank.ACE, Suit.HEARTS),
            Card(Rank.NINE, Suit.CLUBS),
        ]
    )
    assert hand.value() == 21


def test_is_bust_when_total_exceeds_21():
    hand = Hand(
        [
            Card(Rank.TEN, Suit.SPADES),
            Card(Rank.NINE, Suit.HEARTS),
            Card(Rank.FIVE, Suit.CLUBS),
        ]
    )
    assert hand.value() == 24
    assert hand.is_bust is True


def test_is_not_bust_when_total_is_21_or_below():
    hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    assert hand.is_bust is False


def test_two_card_21_is_natural():
    hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])
    assert hand.is_natural is True


def test_21_reached_via_hit_is_not_natural():
    hand = Hand([Card(Rank.SEVEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    hand.add_card(Card(Rank.SEVEN, Suit.CLUBS))
    assert hand.value() == 21
    assert hand.is_natural is False


def test_non_21_two_card_hand_is_not_natural():
    hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    assert hand.is_natural is False
