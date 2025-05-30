from typing import List

from entities.Card import Card
from models.enums.Face import Face
from models.enums.HandResult import HandResult


class Hand():
  __doubled_down: bool
  __finalized: bool
  __from_split: bool
  __bet: int
  __insurance_bet: int
  __result: HandResult
  __cards: List[Card]

  def __init__(self, cards: List[Card], bet: int, from_split: bool):
    self.__doubled_down = False
    self.__finalized = False
    self.__from_split = from_split
    self.__bet = bet
    self.__insurance_bet = 0
    self.__result = HandResult.UNDETERMINED
    self.__cards = cards

  def get_value(self) -> int:
    value = 0
    for card in self.__cards:
      value += card.get_value()
    if value > 21 and self.is_soft():
      for card in self.__cards:
        if card.value_can_reset():
          card.set_value(1)
          break
    return value

  def get_active_ace_count(self) -> int:
    ace_count = 0
    for card in self.__cards:
      if card.get_face() == Face.ACE:
        ace_count += 1
    return ace_count

  def get_bet(self) -> int:
    return self.__bet

  def get_insurance_bet(self) -> int:
    return self.__insurance_bet

  def get_result(self) -> HandResult:
    return self.__result

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

  def double_down(self) -> None:
    if not self.__doubled_down:
      self.__doubled_down = True
      self.__bet *= 2

  def set_bet(self, bet: int) -> None:
    self.__bet = bet

  def set_finalized(self, value=True) -> None:
    self.__finalized = value

  def set_insurance_bet(self, bet: int) -> None:
    self.__insurance_bet = bet

  def set_result(self, result: HandResult) -> None:
    self.__result = result
    self.set_finalized()

  def add_card(self, card: Card) -> None:
    self.__cards.append(card)
    if self.is_soft():
      if self.get_value() > 21:
        self.reset_an_ace()

  def remove_card(self) -> Card:
    card = self.__cards.pop()
    return card

  def reset_an_ace(self) -> None:
    if self.get_value() > 21:
      if self.is_soft():
        for card in self.__cards:
          if card.value_can_reset():
            card.set_value(1)
            break

  def is_soft(self) -> bool:
    for card in self.__cards:
      if card.get_face() == Face.ACE:
        if card.get_value() == 11:
          return True
    return False

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

  def is_insured(self) -> bool:
    return self.__insurance_bet > 0
