from typing import List

from entities.Card import Card
from models.enums.Face import Face


class Hand():
  _cards: List[Card]
  _soft: bool
  _from_split: bool
  _doubled_down: bool
  _finalized: bool
  _value: int
  _active_ace_count: int

  def __init__(self, cards: List[Card], soft: bool, from_split: bool):
    self._cards = cards
    self._soft = soft
    self._from_split = from_split
    self._value = 0
    self._active_ace_count = 0

  def add_card(self, card: Card):
    self._cards.append(card)
    self._value += card.value
    if card.face == Face.ACE:
      self._soft = True
    self._active_ace_count += 1

  def reset_an_ace(self):
    if self._value > 21:
      if self._soft:
        for card in self._cards:
          if card.value_can_reset:
            card.value_can_reset = False
            card.value = 1
            self._active_ace_count -= 1
            break
        if self._active_ace_count == 0:
          self._soft = False

  def is_soft(self):
    return self._soft

  def is_from_split(self):
    return self._from_split

  def is_doubled_down(self):
    return self._doubled_down

  def is_finalized(self):
    return self._finalized

  def get_value(self):
    return self._value

  def get_active_ace_count(self):
    return self._active_ace_count
