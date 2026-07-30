from blackjack.card import Card, Rank, Suit
from blackjack.deck import Deck


def test_deck_has_52_cards():
    assert len(Deck().cards) == 52


def test_deck_cards_are_unique():
    assert len(set(Deck().cards)) == 52


def test_deck_contains_every_rank_and_suit_combination():
    expected = {Card(rank, suit) for rank in Rank for suit in Suit}
    assert set(Deck().cards) == expected
