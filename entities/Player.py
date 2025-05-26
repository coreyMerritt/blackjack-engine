from abc import ABC, abstractmethod
from typing import List
from entities.Hand import Hand
from models.core.GameRules import GameRules


class Player(ABC):
  hands: List[Hand]
  current_bet: int
  money: int
  # TODO: This should be an attribute of a hand, not a player
  doubled_down: bool

  # This can be HumanPlayerInfo or AiPlayerInfo
  # TODO: ^^^ We should probably make a PlayerInfo type and inherit from it
  @abstractmethod
  def __init__(self, player_info) -> None:
    pass

  # TODO: Simpler implementation
  def get_hand_value(self, hand_index: int) -> int:
    value = 0
    for card in self.hands[hand_index]:
      value += card.value

    return value

  def to_dict(self) -> dict:
    return {
      "hand": [c.to_dict() for hand in self.hands for c in hand.cards],
      "current_bet": self.current_bet
    }

  @abstractmethod
  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    pass
