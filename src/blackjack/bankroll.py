from blackjack.bet import Bet, Outcome


class Bankroll:
    """The player's total money across a session."""

    STARTING_BALANCE = 1000

    def __init__(self, balance: int = STARTING_BALANCE) -> None:
        self.balance = balance

    def place_bet(self, amount: int) -> Bet:
        bet = Bet(amount)

        if bet.amount > self.balance:
            raise ValueError("Bet cannot exceed the current bankroll")

        self.balance -= bet.amount
        return bet

    def resolve(self, bet: Bet, outcome: Outcome) -> None:
        self.balance += bet.payout(outcome)
