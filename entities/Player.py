from abc import ABC
from typing import List
from entities.Card import Card
from entities.Hand import Hand
from models.core.PlayerInfo import PlayerInfo


class Player(ABC):
  __hands: List[Hand]
  __money: int

  def __init__(self, player_info: PlayerInfo) -> None:
    self.__hands = []
    self.__money = player_info.money

  def get_hands(self) -> List[Hand]:
    return self.__hands

  def get_money(self) -> int:
    return self.__money

  def get_hand_value(self, hand_index: int) -> int:
    return self.__hands[hand_index].get_value()

  def get_active_hand(self) -> Hand | None:
    for hand in self.__hands:
      if not hand.is_finalized():
        return hand
    return None

  def get_hand_count(self) -> int:
    return len(self.__hands)

  def set_hands(self, hands: List[Hand]) -> None:
    self.__hands = hands

  def set_bet(self, bet: int, hand_index: int) -> None:
    if hand_index + 1 > self.get_hand_count():
      self.add_new_hand(Hand([], bet, False))
    self.__money -= bet

  def add_new_hand(self, hand: Hand) -> None:
    self.__hands.append(hand)

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

  def has_blackjack(self) -> bool:
    if self.get_hand_count() == 1:
      if self.__hands[0].get_card_count() == 2:
        if self.__hands[0].get_card_value() == 21:
          return True
    return False

  def to_dict(self) -> dict:
    return {
      "hand": [c.to_dict() for hand in self.__hands for c in hand.cards],
      "money": self.__money
    }
