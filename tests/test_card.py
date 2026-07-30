from blackjack.card import Card, Rank, Suit


def test_card_has_rank_and_suit():
    card = Card(Rank.ACE, Suit.SPADES)
    assert card.rank is Rank.ACE
    assert card.suit is Suit.SPADES


def test_cards_with_same_rank_and_suit_are_equal():
    assert Card(Rank.KING, Suit.HEARTS) == Card(Rank.KING, Suit.HEARTS)


def test_cards_with_different_rank_or_suit_are_not_equal():
    assert Card(Rank.KING, Suit.HEARTS) != Card(Rank.KING, Suit.SPADES)
    assert Card(Rank.KING, Suit.HEARTS) != Card(Rank.QUEEN, Suit.HEARTS)
