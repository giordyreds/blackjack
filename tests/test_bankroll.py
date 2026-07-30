import pytest

from blackjack.bankroll import Bankroll
from blackjack.bet import Outcome


def test_bankroll_starts_at_1000():
    assert Bankroll().balance == 1000


def test_placing_a_bet_deducts_it_from_the_balance():
    bankroll = Bankroll()
    bankroll.place_bet(50)
    assert bankroll.balance == 950


def test_bet_equal_to_bankroll_is_accepted():
    bankroll = Bankroll(balance=10)
    bankroll.place_bet(10)
    assert bankroll.balance == 0


def test_bet_exceeding_bankroll_raises_and_does_not_deduct():
    bankroll = Bankroll(balance=20)
    with pytest.raises(ValueError):
        bankroll.place_bet(50)
    assert bankroll.balance == 20


def test_resolving_a_natural_credits_three_to_two():
    bankroll = Bankroll()
    bet = bankroll.place_bet(10)
    bankroll.resolve(bet, Outcome.NATURAL)
    assert bankroll.balance == 1015


def test_resolving_a_win_credits_one_to_one():
    bankroll = Bankroll()
    bet = bankroll.place_bet(10)
    bankroll.resolve(bet, Outcome.WIN)
    assert bankroll.balance == 1010


def test_resolving_a_push_returns_the_bet_untouched():
    bankroll = Bankroll()
    bet = bankroll.place_bet(10)
    bankroll.resolve(bet, Outcome.PUSH)
    assert bankroll.balance == 1000


def test_resolving_a_loss_forfeits_the_bet():
    bankroll = Bankroll()
    bet = bankroll.place_bet(10)
    bankroll.resolve(bet, Outcome.LOSS)
    assert bankroll.balance == 990


def test_bankroll_can_reach_zero():
    bankroll = Bankroll(balance=10)
    bet = bankroll.place_bet(10)
    bankroll.resolve(bet, Outcome.LOSS)
    assert bankroll.balance == 0
