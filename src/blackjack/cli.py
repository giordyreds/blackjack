from collections.abc import Callable

from blackjack.bankroll import Bankroll
from blackjack.bet import Bet, Outcome, payout_amount
from blackjack.card import Card
from blackjack.dealer import PeekOutcome, dealer_peek, dealer_should_peek
from blackjack.hand import Hand
from blackjack.round import Action, Round
from blackjack.shoe import Shoe

_OUTCOME_MESSAGES = {
    Outcome.NATURAL: "Natural!",
    Outcome.WIN: "You win.",
    Outcome.PUSH: "Push.",
    Outcome.LOSS: "You lose.",
}


def _format_card(card: Card) -> str:
    return f"{card.rank.value}{card.suit.value[0].upper()}"


def _format_hand(hand: Hand) -> str:
    return ", ".join(_format_card(card) for card in hand.cards)


def _resolve_hand(hand: Hand, dealer_hand: Hand) -> Outcome:
    if hand.is_bust:
        return Outcome.LOSS
    if hand.is_natural and not hand.from_split:
        return Outcome.NATURAL
    if dealer_hand.is_bust:
        return Outcome.WIN
    if hand.value() > dealer_hand.value():
        return Outcome.WIN
    if hand.value() < dealer_hand.value():
        return Outcome.LOSS
    return Outcome.PUSH


def _settle(bankroll: Bankroll, stake: int, outcome: Outcome) -> int:
    payout = payout_amount(stake, outcome)
    bankroll.balance += payout
    return payout


def _prompt_bet(
    bankroll: Bankroll,
    read_line: Callable[[str], str],
    write_line: Callable[[str], None],
) -> Bet | None:
    while True:
        raw = read_line(
            f"Enter your bet (${Bet.MIN_AMOUNT}-${Bet.MAX_AMOUNT}) or 'quit': "
        ).strip().lower()

        if raw in ("q", "quit"):
            return None

        try:
            amount = int(raw)
        except ValueError:
            write_line("Please enter a whole dollar amount.")
            continue

        try:
            return bankroll.place_bet(amount)
        except ValueError as error:
            write_line(str(error))


def _prompt_action(
    round_: Round,
    hand: Hand,
    bet: Bet,
    bankroll: Bankroll,
    doubled_stakes: dict[int, int],
    read_line: Callable[[str], str],
    write_line: Callable[[str], None],
) -> Action:
    while True:
        write_line(f"Your hand: {_format_hand(hand)} ({hand.value()})")

        options = {"h": Action.HIT, "s": Action.STAND}
        prompt_parts = ["[H]it", "[S]tand"]

        if round_.can_double_down(hand) and bankroll.balance >= bet.amount:
            options["d"] = Action.DOUBLE_DOWN
            prompt_parts.append("[D]ouble")

        if round_.can_split(hand) and bankroll.balance >= bet.amount:
            options["p"] = Action.SPLIT
            prompt_parts.append("s[P]lit")

        choice = read_line(f"{' '.join(prompt_parts)}? ").strip().lower()[:1]

        if choice not in options:
            write_line("Please choose one of the listed actions.")
            continue

        action = options[choice]

        if action is Action.DOUBLE_DOWN:
            bankroll.balance -= bet.amount
            doubled_stakes[id(hand)] = bet.amount * 2
        elif action is Action.SPLIT:
            bankroll.balance -= bet.amount

        return action


def _play_round(
    bankroll: Bankroll,
    bet: Bet,
    shoe: Shoe,
    read_line: Callable[[str], str],
    write_line: Callable[[str], None],
) -> None:
    round_ = Round(shoe)
    round_.deal_initial()

    write_line(f"Your hand: {_format_hand(round_.player_hand)}")
    write_line(f"Dealer shows: {_format_card(round_.dealer_hand.cards[0])}")

    if dealer_should_peek(round_.dealer_hand.cards[0]):
        write_line("Dealer peeks at the hole card...")
        peek_outcome = dealer_peek(round_.player_hand, round_.dealer_hand)

        if peek_outcome is not None:
            write_line(f"Dealer's hand: {_format_hand(round_.dealer_hand)}")
            outcome = Outcome.PUSH if peek_outcome is PeekOutcome.PUSH else Outcome.LOSS
            payout = _settle(bankroll, bet.amount, outcome)
            write_line(f"{_OUTCOME_MESSAGES[outcome]} You get back ${payout}.")
            write_line(f"Bankroll: ${bankroll.balance}")
            return

        write_line("No natural. Play continues.")

    doubled_stakes: dict[int, int] = {}

    def decide(hand: Hand) -> Action:
        return _prompt_action(round_, hand, bet, bankroll, doubled_stakes, read_line, write_line)

    round_.play_player_turn(decide)
    round_.play_dealer_turn()

    write_line(
        f"Dealer's hand: {_format_hand(round_.dealer_hand)} ({round_.dealer_hand.value()})"
    )

    for hand in round_.player_hands:
        stake = doubled_stakes.get(id(hand), bet.amount)
        outcome = _resolve_hand(hand, round_.dealer_hand)
        payout = _settle(bankroll, stake, outcome)
        write_line(
            f"{_format_hand(hand)} ({hand.value()}) -- {_OUTCOME_MESSAGES[outcome]} "
            f"You get back ${payout}."
        )

    write_line(f"Bankroll: ${bankroll.balance}")


def main(
    bankroll: Bankroll | None = None,
    shoe: Shoe | None = None,
    read_line: Callable[[str], str] = input,
    write_line: Callable[[str], None] = print,
) -> None:
    bankroll = bankroll if bankroll is not None else Bankroll()
    shoe = shoe if shoe is not None else Shoe()

    write_line("Welcome to Blackjack! Naturals pay 3:2.")

    while True:
        if bankroll.balance <= 0:
            write_line("You're out of money. Game over.")
            return

        if bankroll.balance < Bet.MIN_AMOUNT:
            write_line(
                f"Your bankroll (${bankroll.balance}) is below the "
                f"${Bet.MIN_AMOUNT} minimum bet. Game over."
            )
            return

        write_line(f"\nBankroll: ${bankroll.balance}")
        bet = _prompt_bet(bankroll, read_line, write_line)

        if bet is None:
            write_line(f"Thanks for playing! Final bankroll: ${bankroll.balance}.")
            return

        _play_round(bankroll, bet, shoe, read_line, write_line)


if __name__ == "__main__":
    main()
