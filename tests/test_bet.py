import pytest

from blackjack.bet import Bet, Outcome


def test_bet_within_range_is_accepted():
    bet = Bet(50)
    assert bet.amount == 50


def test_bet_below_minimum_raises():
    with pytest.raises(ValueError):
        Bet(9)


def test_bet_above_maximum_raises():
    with pytest.raises(ValueError):
        Bet(501)


def test_bet_at_minimum_boundary_is_accepted():
    assert Bet(10).amount == 10


def test_bet_at_maximum_boundary_is_accepted():
    assert Bet(500).amount == 500


def test_natural_pays_three_to_two_including_original_stake():
    assert Bet(10).payout(Outcome.NATURAL) == 25


def test_win_pays_one_to_one_including_original_stake():
    assert Bet(10).payout(Outcome.WIN) == 20


def test_push_returns_original_stake():
    assert Bet(10).payout(Outcome.PUSH) == 10


def test_loss_forfeits_stake():
    assert Bet(10).payout(Outcome.LOSS) == 0


def test_natural_payout_on_an_odd_amount_rounds_down():
    assert Bet(11).payout(Outcome.NATURAL) == 27
