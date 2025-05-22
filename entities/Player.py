from abc import ABC, abstractmethod
from typing import List
from entities.Card import Card

class Player(ABC):
  hand: List[Card]
  current_bet: int

  def __init__(self):
    self.hand: List[Card] = []
    self.money: int
    self.current_bet: int

  @abstractmethod
  def place_bet(self, min_possible, max_possible, bet=None):
    pass

  def to_dict(self):
    return {
      "hand": [h.to_dict() for h in self.hand],
      "current_bet": self.current_bet
    }
