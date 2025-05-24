from abc import ABC, abstractmethod
from typing import List
from entities.Card import Card
from models.core.PlayerInfo import PlayerInfo


class Player(ABC):
  hand: List[Card]
  current_bet: int
  money: int
  doubled_down: bool

  def __init__(self, player_info: PlayerInfo) -> None:
    self.hand: List[Card] = []
    self.money = player_info.money
    self.current_bet = 0
    self.doubled_down = False

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
  def place_bet(self, min_possible, max_possible, bet=None) -> None:
    pass
