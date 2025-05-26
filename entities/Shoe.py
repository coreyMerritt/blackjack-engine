from typing import List
from entities.Card import Card

class Shoe:
  _deck_count: int
  _full_size: int
  _reset_percentage: int
  _cards: List[Card]

  def __init__(self, deck_count: int, reset_percentage: int) -> None:
    self._deck_count = deck_count
    self._full_size = deck_count * 52
    self._reset_percentage = reset_percentage
    self._cards = []

  def get_full_size(self) -> int:
    return self._full_size

  def get_card_count(self) -> int:
    return len(self._cards)

  def get_reset_percentage(self) -> int:
    return self._reset_percentage

  def draw(self) -> Card:
    return self._cards.pop()

  def to_dict(self) -> dict:
    return {
      "full_size": self._full_size,
      "previous_deck_count": self._deck_count,
      "reset_percentage": self._reset_percentage,
      "cards": [c.to_dict() for c in self._cards]
    }
