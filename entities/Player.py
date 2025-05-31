from abc import ABC
from typing import List
from uuid import UUID, uuid4
from entities.Card import Card
from entities.Hand import Hand
from models.core.BetSpread import BetSpread
from models.core.player_info.PlayerInfo import PlayerInfo
from models.enums.HandResult import HandResult
from services.BlackjackLogger import BlackjackLogger


class Player(ABC):
  __id: UUID
  __bankroll: int
  __hands: List[Hand]

  def __init__(self, player_info: PlayerInfo) -> None:
    self.__hands = []
    self.__bankroll = player_info.bankroll
    self.__id = uuid4()

  def get_id(self) -> UUID:
    return self.__id

  def get_hand(self, hand_index: int) -> Hand:
    return self.__hands[hand_index]

  def get_hands(self) -> List[Hand]:
    return self.__hands

  def get_bankroll(self) -> int:
    return self.__bankroll

  def get_hand_value(self, hand_index: int) -> int:
    assert hand_index + 1 <= self.get_hand_count()
    return self.__hands[hand_index].get_value()

  def get_active_hand(self) -> Hand | None:
    for hand in self.__hands:
      if not hand.is_finalized():
        assert hand.get_result() == HandResult.UNDETERMINED
        return hand
    return None

  def get_hand_count(self) -> int:
    return len(self.__hands)

  def get_hand_index(self, hand: Hand) -> int:
    for i, my_hand in enumerate(self.__hands):
      if hand == my_hand:
        return i

  def get_bet_spread(self) -> BetSpread | None:
    return None

  def set_hands(self, hands: List[Hand]) -> None:
    self.__hands = hands

  def set_bet(self, bet: int, hand_index: int) -> None:
    if hand_index + 1 > self.get_hand_count():
      self.add_new_hand(Hand([], bet, False))
    self.decrement_bankroll(bet)

  def add_new_hand(self, hand: Hand) -> None:
    self.__hands.append(hand)

  def increment_bankroll(self, amount: int, silent=False) -> None:
    if amount != 0:
      if not silent:
        BlackjackLogger.debug(f"\t\tAdjusting bankroll from: {self.__bankroll} -> {self.__bankroll + amount}")
      self.__bankroll += amount

  def decrement_bankroll(self, amount: int, silent=False) -> None:
    if amount != 0:
      if not silent:
        BlackjackLogger.debug(f"\t\tAdjusting bankroll from: {self.__bankroll} -> {self.__bankroll - amount}")
      self.__bankroll -= amount

  def update_running_count(self, card_value: int) -> None:
    pass

  def add_to_active_hand(self, card: Card) -> None:
    active_hand = self.get_active_hand()
    active_hand.add_card(card)

  def finalize_active_hand(self) -> None:
    active_hand = self.get_active_hand()
    active_hand.set_finalized()

  def has_active_hand(self) -> bool:
    for hand in self.__hands:
      if not hand.is_finalized():
        return True
    return False

  def has_blackjack(self) -> bool:
    if self.get_hand_count() == 1:
      if self.__hands[0].get_card_count() == 2:
        if self.get_hand_value(0) == 21:
          return True
    return False

  def to_dict(self) -> dict:
    return {
      "hand": [c.to_dict() for hand in self.__hands for c in hand.get_cards()],
      "bankroll": self.__bankroll
    }
