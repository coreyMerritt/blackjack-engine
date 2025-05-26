from abc import ABC
from typing import List
from entities.Card import Card
from entities.Hand import Hand
from models.core.PlayerInfo import PlayerInfo


class Player(ABC):
  __hands: List[Hand]
  __money: int
  # TODO: This should be an attribute of a hand, not a player
  __doubled_down: bool

  def __init__(self, player_info: PlayerInfo) -> None:
    self.__hands = []
    self.__money = player_info.money
    self.__bet = 0
    self.__doubled_down = False

  def get_hands(self) -> List[Hand]:
    return self.__hands

  def get_current_bet(self) -> int:
    return self.__bet

  def get_money(self) -> int:
    return self.__money

  # TODO: Get rid of this member completely
  def get_doubled_down(self) -> bool:
    return self.__doubled_down

  # TODO: Simpler implementation
  def get_hand_value(self, hand_index: int) -> int:
    value = 0
    for card in self.__hands[hand_index]:
      value += card.value

    return value

  def get_active_hand(self) -> Hand | None:
    for hand in self.__hands:
      if not hand.is_finalized():
        return hand
    return None

  def set_hands(self, hands: List[Hand]) -> None:
    self.__hands = hands

  def set_bet(self, bet: int, hand_index: int) -> None:
    self.__hands[hand_index].set_bet(bet)

  def increment_money(self, amount: int) -> None:
    self.__money += amount

  def decrement_money(self, amount: int) -> None:
    self.__money -= amount

  def add_to_active_hand(self, card: Card) -> None:
    active_hand = self.get_active_hand()
    active_hand.add_card(card)

  def finalize_active_hand(self) -> None:
    active_hand = self.get_active_hand()
    active_hand.set_finalized(True)

  def has_active_hand(self) -> bool:
    for hand in self.__hands:
      if not hand.is_finalized():
        return True
    return False

  def to_dict(self) -> dict:
    return {
      "hand": [c.to_dict() for hand in self.__hands for c in hand.cards],
      "current_bet": self.__bet
    }
