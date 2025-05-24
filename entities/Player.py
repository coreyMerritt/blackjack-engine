from abc import ABC, abstractmethod
from typing import List
from entities.Card import Card
from models.core.GameRules import GameRules


class Player(ABC):
  hand: List[Card]
  current_bet: int
  money: int
  doubled_down: bool

  # This can be HumanPlayerInfo or AiPlayerInfo
  @abstractmethod
  def __init__(self, human_player_info) -> None:
    pass

  def get_hand_value(self) -> int:
    value = 0
    for card in self.hand:
      value += card.value

    return value

  def to_dict(self) -> dict:
    return {
      "hand": [h.to_dict() for h in self.hand],
      "current_bet": self.current_bet
    }

  @abstractmethod
  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    pass
