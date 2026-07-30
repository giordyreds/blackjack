from collections.abc import Callable
from enum import Enum

from blackjack.card import Rank
from blackjack.hand import Hand
from blackjack.shoe import Shoe

DEALER_STAND_THRESHOLD = 17
MAX_PLAYER_HANDS = 3


class Action(Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE_DOWN = "double_down"
    SPLIT = "split"


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
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()

    @property
    def player_hand(self) -> Hand:
        return self.player_hands[0]

    @player_hand.setter
    def player_hand(self, hand: Hand) -> None:
        self.player_hands[0] = hand

    def deal_initial(self) -> None:
        for _ in range(2):
            self.player_hand.add_card(self.shoe.deal())
            self.dealer_hand.add_card(self.shoe.deal())

    def can_split(self, hand: Hand) -> bool:
        return (
            hand.is_pair
            and not hand.is_split_aces
            and len(self.player_hands) < MAX_PLAYER_HANDS
        )

    def can_double_down(self, hand: Hand) -> bool:
        return len(hand.cards) == 2

    def play_player_turn(self, decide: PlayerDecision) -> None:
        if self.player_hand.is_natural:
            return

        index = 0
        while index < len(self.player_hands):
            self._play_hand(index, decide)
            index += 1

    def _play_hand(self, index: int, decide: PlayerDecision) -> None:
        hand = self.player_hands[index]

        if hand.is_split_aces:
            return

        while True:
            action = decide(hand)

            if action is Action.STAND:
                return

            if action is Action.HIT:
                hand.add_card(self.shoe.deal())
                if hand.is_bust:
                    return
                continue

            if action is Action.DOUBLE_DOWN:
                if not self.can_double_down(hand):
                    raise ValueError("cannot double down on this hand")
                hand.is_doubled = True
                hand.add_card(self.shoe.deal())
                return

            if action is Action.SPLIT:
                if not self.can_split(hand):
                    raise ValueError("cannot split this hand")
                self._split(index)
                hand = self.player_hands[index]
                if hand.is_split_aces:
                    return

    def _split(self, index: int) -> None:
        hand = self.player_hands[index]
        card_a, card_b = hand.cards
        is_aces = card_a.rank is Rank.ACE

        first = Hand([card_a])
        second = Hand([card_b])
        first.from_split = True
        second.from_split = True
        if is_aces:
            first.is_split_aces = True
            second.is_split_aces = True

        self.player_hands[index] = first
        self.player_hands.insert(index + 1, second)

        first.add_card(self.shoe.deal())
        second.add_card(self.shoe.deal())

    def play_dealer_turn(self) -> None:
        if all(hand.is_bust for hand in self.player_hands):
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
