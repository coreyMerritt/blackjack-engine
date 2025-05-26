from typing import List
from entities.Card import Card

class Shoe:
  __deck_count: int
  __full_size: int
  __reset_percentage: int
  __cards: List[Card]

  def __init__(self, deck_count: int, reset_percentage: int) -> None:
    self.__deck_count = deck_count
    self.__full_size = deck_count * 52
    self.__reset_percentage = reset_percentage
    self.__cards = []

  def get_deck_count(self) -> int:
    return self.__deck_count

  def get_full_size(self) -> int:
    return self.__full_size

  def get_card_count(self) -> int:
    return len(self.__cards)

  def get_reset_percentage(self) -> int:
    return self.__reset_percentage

  def draw(self) -> Card:
    return self.__cards.pop()

  def to_dict(self) -> dict:
    return {
      "full_size": self.__full_size,
      "previous_deck_count": self.__deck_count,
      "reset_percentage": self.__reset_percentage,
      "cards": [c.to_dict() for c in self.__cards]
    }
