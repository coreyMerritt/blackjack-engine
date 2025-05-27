from typing import List

from entities.Card import Card
from models.enums.Face import Face


class Hand():
  __cards: List[Card]
  __bet: int
  __from_split: bool
  __doubled_down: bool
  __finalized: bool
  __value: int
  __active_ace_count: int
  __insurance_bet: int

  def __init__(self, cards: List[Card], bet: int, from_split: bool):
    self.__cards = cards
    self.__bet = bet
    self.__soft = False
    self.__from_split = from_split
    self.__value = 0
    self.__active_ace_count = 0
    self.__insurance_bet = 0

  def get_value(self) -> int:
    return self.__value

  def get_active_ace_count(self) -> int:
    return self.__active_ace_count

  def get_bet(self) -> int:
    return self.__bet

  def get_card(self, card_index: int) -> int:
    return self.__cards[card_index]

  def get_cards(self) -> List[Card]:
    return self.__cards

  def get_card_count(self) -> int:
    return len(self.__cards)

  def get_card_face(self, card_index: int) -> Face:
    return self.__cards[card_index].get_face()

  def get_card_value(self, card_index: int) -> int:
    return self.__cards[card_index].get_value()

  def get_insurance_bet(self) -> int:
    return self.__insurance_bet

  def double_down(self) -> None:
    if not self.__doubled_down:
      self.__doubled_down = True
      self.__bet *= 2

  def set_bet(self, bet: int) -> None:
    self.__bet = bet

  def set_finalized(self, value: bool) -> None:
    self.__finalized = value

  def set_insurance_bet(self, bet: int) -> None:
    self.__insurance_bet = bet

  def add_card(self, card: Card) -> None:
    self.__cards.append(card)
    self.__value += card.get_value()
    if card.get_face() == Face.ACE:
      self.__soft = True
    self.__active_ace_count += 1

  def remove_card(self) -> Card:
    card = self.__cards.pop()
    self.__value -= card.get_value()
    self.__active_ace_count -= 1
    if self.get_active_ace_count() == 0:
      self.__soft = False
    return card

  def reset_an_ace(self) -> None:
    if self.__value > 21:
      if self.__soft:
        for card in self.__cards:
          if card.value_can_reset:
            card.value_can_reset = False
            card.set_value(1)
            self.__active_ace_count -= 1
            break
        if self.__active_ace_count == 0:
          self.__soft = False

  def is_soft(self) -> bool:
    return self.__soft

  def is_from_split(self) -> bool:
    return self.__from_split

  def is_doubled_down(self) -> bool:
    return self.__doubled_down

  def is_finalized(self) -> bool:
    return self.__finalized

  def is_pair(self) -> bool:
    return (
      len(self.__cards) == 2
      and self.__cards[0].get_value() == self.__cards[1].get_value()
    )
