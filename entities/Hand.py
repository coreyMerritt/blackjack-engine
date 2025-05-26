from typing import List

from entities.Card import Card
from models.enums.Face import Face


class Hand():
  cards: List[Card]
  hand_is_soft: bool
  is_from_split: bool
  value: int
  active_ace_count: int

  def __init__(self, cards: List[Card], hand_is_soft: bool, is_from_split: bool):
    self.cards = cards
    self.hand_is_soft = hand_is_soft
    self.is_from_split = is_from_split
    self.value = 0
    self.active_ace_count = 0

  def add_card(self, card: Card):
    self.cards.append(card)
    self.value += card.value
    if card.face == Face.ACE:
      self.hand_is_soft = True
    self.active_ace_count += 1

  def reset_an_ace(self):
    if self.value > 21:
      if self.hand_is_soft:
        for card in self.cards:
          if card.value_can_reset:
            card.value_can_reset = False
            card.value = 1
            self.active_ace_count -= 1
            break
        if self.active_ace_count == 0:
          self.hand_is_soft = False
