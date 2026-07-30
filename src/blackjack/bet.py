from enum import Enum


class Outcome(Enum):
    NATURAL = "natural"
    WIN = "win"
    PUSH = "push"
    LOSS = "loss"


# The stake multiplier, as (numerator, denominator), credited back to the
# bankroll for each outcome — including the original stake where it is not
# forfeited. Fractional payouts (e.g. a Natural on an odd-dollar bet) round
# down to the nearest dollar.
_PAYOUT_MULTIPLIERS = {
    Outcome.NATURAL: (5, 2),
    Outcome.WIN: (2, 1),
    Outcome.PUSH: (1, 1),
    Outcome.LOSS: (0, 1),
}


def payout_amount(amount: int, outcome: Outcome) -> int:
    """The amount credited back for a given staked amount and outcome.

    Used directly for stakes that fall outside a Bet's $10-$500 range, such
    as a doubled-down or split hand's stake.
    """
    numerator, denominator = _PAYOUT_MULTIPLIERS[outcome]
    return amount * numerator // denominator


class Bet:
    """The amount staked by the player on a round."""

    MIN_AMOUNT = 10
    MAX_AMOUNT = 500

    def __init__(self, amount: int) -> None:
        if not (self.MIN_AMOUNT <= amount <= self.MAX_AMOUNT):
            raise ValueError(
                f"Bet must be between ${self.MIN_AMOUNT} and ${self.MAX_AMOUNT}"
            )

        self.amount = amount

    def payout(self, outcome: Outcome) -> int:
        return payout_amount(self.amount, outcome)
