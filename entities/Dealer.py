from random import shuffle
from typing import List
from entities.Player import Player
from entities.Card import Card, Face, Suit

class Dealer:
  shoe: List[Card]
  full_shoe_size: int
  hand: List[Card]
  previous_deck_count: int

  def __init__(self):
    self.shoe = []
    self.hand = []

  def load_shoe(self, deck_count: int) -> List[str]:
    self.previous_deck_count = deck_count
    self.shoe = []

    for _ in range(deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.append(card)

    self.full_shoe_size = 52 * deck_count
    assert self.full_shoe_size == len(self.shoe)

  def deal(self, players: List[Player], shoe_reset_percentage: int):
    shoe_is_above_reset_point = len(self.shoe) > (self.full_shoe_size / (100 / shoe_reset_percentage))
    if not shoe_is_above_reset_point:
      self.shuffle_shoe()

    for player in players:
      for _ in range(2):
        player.hand.append(self.shoe.pop())

  def shuffle_shoe(self):
    self.load_shoe(self.previous_deck_count)
    shuffle(self.shoe)
