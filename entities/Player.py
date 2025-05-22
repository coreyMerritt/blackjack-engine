from abc import ABC, abstractmethod
from enum import Enum
from typing import List
from services.ServerLogger import ServerLogger
from entities.Card import Card

class PlayerDecisions(Enum):
  PLACEHOLDER = 0
  HIT = 1
  STAND = 2

class Player(ABC):
  hand: List[Card]
  current_bet: int

  def __init__(self):
    self.hand: List[Card] = []
    self.money: int
    self.current_bet: int

  def get_hand_value(self):
    value = 0
    for card in self.hand:
      value += card.value
      ServerLogger.debug(value)

    return value

  @abstractmethod
  def place_bet(self, min_possible, max_possible, bet=None):
    pass

  def to_dict(self):
    return {
      "hand": [h.to_dict() for h in self.hand],
      "current_bet": self.current_bet
    }
