from typing import List
from entities.Card import Card

class Shoe:
  cards: List[Card]
  reset_percentage: int
  full_size: int
  previous_deck_count: int

  def __init__(self):
    self.cards = []
