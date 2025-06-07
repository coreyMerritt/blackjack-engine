from abc import ABC
from typing import List
from uuid import UUID, uuid4
from entities.Card import Card
from entities.Hand import Hand
from models.core.player_info.PlayerInfo import PlayerInfo
from models.enums.HandResult import HandResult
from services.BlackjackLogger import BlackjackLogger


class Player(ABC):
  __bankroll: float
  __id: UUID
  __hands: List[Hand]

  def __init__(self, player_info: PlayerInfo):
    self.__hands = []
    self.__bankroll = float(player_info.bankroll)
    self.__id = uuid4()

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

  def get_bankroll(self) -> float:
    return self.__bankroll

  def get_hand_value(self, hand_index: int) -> int:
    assert hand_index + 1 <= self.get_hand_count()
    return self.__hands[hand_index].get_value()

  def get_hand_count(self) -> int:
    return len(self.__hands)

  def get_hand_index(self, hand: Hand) -> int:
    for i, my_hand in enumerate(self.__hands):
      if hand == my_hand:
        return i

  def get_id(self) -> str:
    return str(self.__id)

  def get_hand(self, hand_index: int) -> Hand:
    return self.__hands[hand_index]

  def get_hands(self) -> List[Hand]:
    return self.__hands

  def calculate_active_hand(self) -> Hand:
    for hand in self.__hands:
      if not hand.is_finalized():
        assert hand.get_result() == HandResult.UNDETERMINED
        return hand
    raise RuntimeError("Tried to calculate the active_hand of a player with no active_hand")

  def set_hands(self, hands: List[Hand]) -> None:
    self.__hands = hands

  def add_to_active_hand(self, card: Card) -> None:
    active_hand = self.calculate_active_hand()
    active_hand.add_card(card)

  def add_new_hand(self, hand: Hand) -> None:
    self.__hands.append(hand)

  def increment_bankroll(self, amount: float, silent=False) -> None:
    if amount != 0:
      if not silent:
        BlackjackLogger.debug(f"\t\tAdjusting bankroll from: {self.__bankroll} -> {self.__bankroll + amount}")
      self.__bankroll += amount

  def decrement_bankroll(self, amount: float, silent=False) -> None:
    if amount != 0:
      if not silent:
        BlackjackLogger.debug(f"\t\tAdjusting bankroll from: {self.__bankroll} -> {self.__bankroll - amount}")
      self.__bankroll -= amount

  def to_dict(self) -> dict:
    return {
      "id": str(self.__id),
      "bankroll": self.__bankroll,
      "hands": [hand.to_dict() for hand in self.__hands]
    }
