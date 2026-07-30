import random
from collections import Counter

from blackjack.card import Card
from blackjack.deck import Deck
from blackjack.shoe import Shoe

CARDS_PER_SHOE = 312
DEFAULT_CUT_CARD_POSITION = 234  # 312 * 0.75


def test_shoe_holds_six_decks_worth_of_cards():
    shoe = Shoe(penetration=1.0)
    assert shoe.cards_remaining == CARDS_PER_SHOE


def test_shoe_is_composed_of_six_copies_of_a_standard_deck():
    shoe = Shoe(penetration=1.0)
    dealt = [shoe.deal() for _ in range(CARDS_PER_SHOE)]
    assert Counter(dealt) == Counter(Deck().cards * 6)


def test_shoe_shuffles_the_cards():
    unshuffled = Deck().cards * 6
    shoe = Shoe(rng=random.Random(42), penetration=1.0)
    dealt = [shoe.deal() for _ in range(CARDS_PER_SHOE)]
    assert dealt != unshuffled


def test_shoe_deals_one_card_at_a_time():
    shoe = Shoe(penetration=1.0)
    card = shoe.deal()
    assert isinstance(card, Card)
    assert shoe.cards_remaining == CARDS_PER_SHOE - 1


def test_shoe_reshuffles_once_default_penetration_is_reached():
    shoe = Shoe()
    for _ in range(DEFAULT_CUT_CARD_POSITION):
        shoe.deal()
    assert shoe.cards_remaining == CARDS_PER_SHOE - DEFAULT_CUT_CARD_POSITION

    shoe.deal()
    assert shoe.cards_remaining == CARDS_PER_SHOE - 1


def test_shoe_reshuffles_once_custom_penetration_is_reached():
    shoe = Shoe(penetration=0.5)
    for _ in range(156):
        shoe.deal()
    assert shoe.cards_remaining == CARDS_PER_SHOE - 156

    shoe.deal()
    assert shoe.cards_remaining == CARDS_PER_SHOE - 1
