from abc import ABC, abstractmethod
from typing import List
from entities.Card import Card

class Player(ABC):
  hand: List[Card]

  def __init__(self):
    self.hand: List[Card] = []
    self.money: int
    self.current_bet: int

  @abstractmethod
  def place_bet(self, min_possible, max_possible, bet=None):
    pass