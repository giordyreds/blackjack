from blackjack.card import Card, Rank, Suit
from blackjack.dealer import PeekOutcome, dealer_peek, dealer_should_peek
from blackjack.hand import Hand


def test_peek_triggers_on_ace_up_card():
    assert dealer_should_peek(Card(Rank.ACE, Suit.SPADES)) is True


def test_peek_triggers_on_ten_value_up_card():
    for rank in (Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING):
        assert dealer_should_peek(Card(rank, Suit.SPADES)) is True


def test_peek_does_not_trigger_on_low_up_card():
    for rank in (Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN, Rank.EIGHT, Rank.NINE):
        assert dealer_should_peek(Card(rank, Suit.SPADES)) is False


def test_no_peek_trigger_means_round_continues_regardless_of_hands():
    player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)])
    dealer_hand = Hand([Card(Rank.SEVEN, Suit.CLUBS), Card(Rank.NINE, Suit.DIAMONDS)])

    assert dealer_peek(player_hand, dealer_hand) is None


def test_dealer_natural_found_by_peek_ends_round_as_dealer_win():
    player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    dealer_hand = Hand([Card(Rank.ACE, Suit.CLUBS), Card(Rank.KING, Suit.DIAMONDS)])

    assert dealer_peek(player_hand, dealer_hand) is PeekOutcome.DEALER_WINS


def test_peek_triggers_but_dealer_has_no_natural_continues_round():
    player_hand = Hand([Card(Rank.TEN, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)])
    dealer_hand = Hand([Card(Rank.ACE, Suit.CLUBS), Card(Rank.NINE, Suit.DIAMONDS)])

    assert dealer_peek(player_hand, dealer_hand) is None


def test_player_natural_alone_does_not_end_the_round_via_peek():
    player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS)])
    dealer_hand = Hand([Card(Rank.ACE, Suit.CLUBS), Card(Rank.NINE, Suit.DIAMONDS)])

    assert dealer_peek(player_hand, dealer_hand) is None


def test_player_natural_and_dealer_natural_is_a_push():
    player_hand = Hand([Card(Rank.ACE, Suit.SPADES), Card(Rank.QUEEN, Suit.HEARTS)])
    dealer_hand = Hand([Card(Rank.TEN, Suit.CLUBS), Card(Rank.ACE, Suit.DIAMONDS)])

    assert dealer_peek(player_hand, dealer_hand) is PeekOutcome.PUSH
