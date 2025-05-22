from random import shuffle
from typing import List
from entities.Shoe import Shoe
from entities.Player import Player
from entities.Card import Card, Face, Suit

class Dealer:
  shoe: Shoe
  hand: List[Card]

  def __init__(self):
    self.hand = []
    self.shoe = Shoe()

  def deal(self, players: List[Player]):
    for player in players:
      for _ in range(2):
        player.hand.append(self.shoe.cards.pop())

  def shuffle_shoe(self):
    shuffle(self.shoe.cards)

  def load_shoe(self, deck_count: int) -> List[str]:
    self.shoe.previous_deck_count = deck_count
    self.shoe.cards = []

    for _ in range(deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.cards.append(card)

    self.shoe.full_size = 52 * deck_count
    assert self.shoe.full_size == len(self.shoe.cards)
