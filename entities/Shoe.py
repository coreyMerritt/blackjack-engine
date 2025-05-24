from typing import List
from entities.Card import Card

class Shoe:
  full_size: int
  deck_count: int
  reset_percentage: int
  cards: List[Card]

  def __init__(self, deck_count) -> None:
    self.deck_count = deck_count
    self.cards = []

  def to_dict(self) -> dict:
    return {
      "full_size": self.full_size,
      "previous_deck_count": self.deck_count,
      "reset_percentage": self.reset_percentage,
      "cards": [c.to_dict() for c in self.cards]
    }
