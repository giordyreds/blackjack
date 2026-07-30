from collections.abc import Callable
from enum import Enum

from blackjack.hand import Hand
from blackjack.shoe import Shoe

DEALER_STAND_THRESHOLD = 17


class Action(Enum):
    HIT = "hit"
    STAND = "stand"


class Outcome(Enum):
    PLAYER_BUST = "player_bust"
    DEALER_BUST = "dealer_bust"
    PLAYER_NATURAL = "player_natural"
    PLAYER_WIN = "player_win"
    DEALER_WIN = "dealer_win"
    PUSH = "push"


PlayerDecision = Callable[[Hand], Action]


class Round:
    """A single hand of blackjack: deal, player turn, dealer turn, outcome."""

    def __init__(self, shoe: Shoe) -> None:
        self.shoe = shoe
        self.player_hand = Hand()
        self.dealer_hand = Hand()

    def deal_initial(self) -> None:
        for _ in range(2):
            self.player_hand.add_card(self.shoe.deal())
            self.dealer_hand.add_card(self.shoe.deal())

    def play_player_turn(self, decide: PlayerDecision) -> None:
        if self.player_hand.is_natural:
            return

        while decide(self.player_hand) is Action.HIT:
            self.player_hand.add_card(self.shoe.deal())
            if self.player_hand.is_bust:
                return

    def play_dealer_turn(self) -> None:
        if self.player_hand.is_bust:
            return

        while self.dealer_hand.value() < DEALER_STAND_THRESHOLD:
            self.dealer_hand.add_card(self.shoe.deal())

    def resolve(self) -> Outcome:
        if self.player_hand.is_bust:
            return Outcome.PLAYER_BUST
        if self.dealer_hand.is_bust:
            return Outcome.DEALER_BUST

        if self.player_hand.is_natural or self.dealer_hand.is_natural:
            if self.player_hand.is_natural and not self.dealer_hand.is_natural:
                return Outcome.PLAYER_NATURAL
            if self.dealer_hand.is_natural and not self.player_hand.is_natural:
                return Outcome.DEALER_WIN
            return Outcome.PUSH

        player_value = self.player_hand.value()
        dealer_value = self.dealer_hand.value()
        if player_value > dealer_value:
            return Outcome.PLAYER_WIN
        if player_value < dealer_value:
            return Outcome.DEALER_WIN
        return Outcome.PUSH

    def play(self, decide: PlayerDecision) -> Outcome:
        self.deal_initial()
        self.play_player_turn(decide)
        self.play_dealer_turn()
        return self.resolve()
