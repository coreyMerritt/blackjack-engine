from typing import List
from entities.Card import Card

class Player:
  hand: List[Card]

  def __init__(self):
    self.hand: List[Card] = []
