from blackjack.bankroll import Bankroll
from blackjack.card import Card, Rank, Suit
from blackjack.cli import main


class StubShoe:
    """Deals a predetermined sequence of cards, in order."""

    def __init__(self, cards: list[Card]) -> None:
        self._cards = list(cards)

    def deal(self) -> Card:
        return self._cards.pop(0)


def scripted_input(*responses: str):
    remaining = list(responses)
    prompts: list[str] = []

    def read_line(prompt: str) -> str:
        prompts.append(prompt)
        return remaining.pop(0)

    read_line.prompts = prompts
    return read_line


def collecting_output():
    messages: list[str] = []

    def write_line(message: str) -> None:
        messages.append(message)

    return write_line, messages


def test_quits_immediately_without_playing_a_round():
    bankroll = Bankroll()
    read_line = scripted_input("quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=StubShoe([]), read_line=read_line, write_line=write_line)

    assert bankroll.balance == 1000
    assert any("Thanks for playing" in message for message in messages)


def test_full_round_end_to_end_bet_deal_peek_actions_dealer_play_payout():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.TEN, Suit.SPADES),  # player
            Card(Rank.FIVE, Suit.CLUBS),  # dealer up card
            Card(Rank.NINE, Suit.HEARTS),  # player
            Card(Rank.SIX, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.SIX, Suit.SPADES),  # dealer hits to 17
        ]
    )
    read_line = scripted_input("50", "s", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 1050
    assert any("You win." in message for message in messages)
    assert any("Thanks for playing! Final bankroll: $1050." in message for message in messages)


def test_invalid_bets_are_rejected_and_a_natural_pays_three_to_two():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.ACE, Suit.SPADES),  # player
            Card(Rank.NINE, Suit.CLUBS),  # dealer up card (no peek)
            Card(Rank.KING, Suit.HEARTS),  # player
            Card(Rank.TWO, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.SIX, Suit.HEARTS),  # dealer hits to 17
        ]
    )
    read_line = scripted_input("5", "abc", "10", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 1015
    assert any("Bet must be between $10 and $500" in message for message in messages)
    assert any("Please enter a whole dollar amount." in message for message in messages)
    assert any("Natural!" in message for message in messages)


def test_bankroll_reaching_zero_ends_the_game_without_further_prompts():
    bankroll = Bankroll(balance=10)
    shoe = StubShoe(
        [
            Card(Rank.TEN, Suit.SPADES),  # player
            Card(Rank.FIVE, Suit.CLUBS),  # dealer up card (no peek)
            Card(Rank.SEVEN, Suit.HEARTS),  # player
            Card(Rank.SIX, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.NINE, Suit.CLUBS),  # player hits and busts
        ]
    )
    read_line = scripted_input("10", "h")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 0
    assert any("out of money" in message.lower() for message in messages)


def test_double_down_doubles_the_stake_and_deals_one_card():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.FIVE, Suit.SPADES),  # player
            Card(Rank.FOUR, Suit.CLUBS),  # dealer up card (no peek)
            Card(Rank.SIX, Suit.HEARTS),  # player
            Card(Rank.THREE, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.NINE, Suit.CLUBS),  # double-down card
            Card(Rank.SIX, Suit.SPADES),  # dealer hits
            Card(Rank.FIVE, Suit.DIAMONDS),  # dealer hits to 18
        ]
    )
    read_line = scripted_input("20", "d", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert "[D]ouble" in read_line.prompts[1]
    assert bankroll.balance == 1040
    assert any("You win." in message for message in messages)


def test_split_creates_two_hands_settled_independently():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.EIGHT, Suit.SPADES),  # player
            Card(Rank.FOUR, Suit.CLUBS),  # dealer up card (no peek)
            Card(Rank.EIGHT, Suit.HEARTS),  # player
            Card(Rank.THREE, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.NINE, Suit.CLUBS),  # dealt to first split hand
            Card(Rank.SIX, Suit.SPADES),  # dealt to second split hand
            Card(Rank.FIVE, Suit.DIAMONDS),  # dealer hits
            Card(Rank.FIVE, Suit.HEARTS),  # dealer hits to 17
        ]
    )
    read_line = scripted_input("30", "p", "s", "s", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert "s[P]lit" in read_line.prompts[1]
    assert bankroll.balance == 970
    assert any("Push." in message for message in messages)
    assert any("You lose." in message for message in messages)


def test_split_hand_reaching_21_pays_as_a_regular_win_not_a_natural():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.TEN, Suit.SPADES),  # player
            Card(Rank.FOUR, Suit.CLUBS),  # dealer up card (no peek)
            Card(Rank.TEN, Suit.HEARTS),  # player
            Card(Rank.THREE, Suit.DIAMONDS),  # dealer hole card
            Card(Rank.ACE, Suit.CLUBS),  # dealt to first split hand -- 21, but not a Natural
            Card(Rank.TWO, Suit.DIAMONDS),  # dealt to second split hand
            Card(Rank.FIVE, Suit.DIAMONDS),  # dealer hits
            Card(Rank.SIX, Suit.SPADES),  # dealer hits to 18
        ]
    )
    read_line = scripted_input("30", "p", "s", "s", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 1000
    assert any("21) -- You win." in message for message in messages)
    assert not any("Natural!" in message for message in messages)


def test_dealer_peek_natural_ends_the_round_before_player_acts():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.TEN, Suit.SPADES),  # player
            Card(Rank.ACE, Suit.CLUBS),  # dealer up card (triggers peek)
            Card(Rank.SIX, Suit.HEARTS),  # player
            Card(Rank.KING, Suit.DIAMONDS),  # dealer hole card completes a natural
        ]
    )
    read_line = scripted_input("10", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 990
    assert any("Dealer peeks at the hole card" in message for message in messages)
    assert any("You lose." in message for message in messages)


def test_dealer_peek_both_naturals_is_a_push():
    bankroll = Bankroll()
    shoe = StubShoe(
        [
            Card(Rank.ACE, Suit.SPADES),  # player
            Card(Rank.TEN, Suit.CLUBS),  # dealer up card (triggers peek)
            Card(Rank.KING, Suit.HEARTS),  # player
            Card(Rank.ACE, Suit.DIAMONDS),  # dealer hole card completes a natural
        ]
    )
    read_line = scripted_input("10", "quit")
    write_line, messages = collecting_output()

    main(bankroll=bankroll, shoe=shoe, read_line=read_line, write_line=write_line)

    assert bankroll.balance == 1000
    assert any("Push." in message for message in messages)
