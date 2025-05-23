from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from entities.Card import Card
from models.api.PlayerInfo import PlayerInfo

class PlayerDecisions(Enum):
  PLACEHOLDER = 0
  HIT = 1
  STAND = 2

class Player(ABC):
  hand: List[Card]
  current_bet: int
  money: int

  def __init__(self, player_info: PlayerInfo):
    self.hand: List[Card] = []
    self.money = player_info.money
    self.current_bet = 0

  def get_hand_value(self):
    value = 0
    for card in self.hand:
      value += card.value

    return value

  @abstractmethod
  def place_bet(self, min_possible, max_possible, bet=None):
    pass

  def to_dict(self):
    return {
      "hand": [h.to_dict() for h in self.hand],
      "current_bet": self.current_bet
    }
