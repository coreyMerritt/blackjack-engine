from abc import ABC, abstractmethod
from typing import List
from entities.Card import Card
from entities.Hand import Hand
from models.core.GameRules import GameRules


class Player(ABC):
  _hands: List[Hand]
  _current_bet: int
  _money: int
  # TODO: This should be an attribute of a hand, not a player
  _doubled_down: bool

  def get_hands(self) -> List[Hand]:
    return self._hands

  # TODO: Simpler implementation
  def get_hand_value(self, hand_index: int) -> int:
    value = 0
    for card in self._hands[hand_index]:
      value += card.value

    return value

  def get_active_hand(self) -> Hand | None:
    for hand in self._hands:
      if hand.is_finalized():
        continue
      return hand
    return None

  def add_to_active_hand(self, card: Card) -> None:
    active_hand = self.get_active_hand()
    active_hand.add_card(card)

  def to_dict(self) -> dict:
    return {
      "hand": [c.to_dict() for hand in self._hands for c in hand.cards],
      "current_bet": self._current_bet
    }

  # This can be HumanPlayerInfo or AiPlayerInfo
  # TODO: ^^^ We should probably make a PlayerInfo type and inherit from it
  @abstractmethod
  def __init__(self, player_info) -> None:
    pass

  @abstractmethod
  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    pass
