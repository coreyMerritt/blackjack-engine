from random import shuffle
from typing import List
from entities.Shoe import Shoe
from entities.Player import Player
from entities.Card import Card, Face, Suit

class Dealer:
  shoe: Shoe
  hand: List[Card]

  def __init__(self, deck_count):
    self.hand = []
    self.shoe = Shoe(deck_count)

  def deal(self, players: List[Player]):
    for player in players:
      for _ in range(2):
        player.hand.append(self.shoe.cards.pop())

  def shuffle_shoe(self):
    shuffle(self.shoe.cards)

  def load_shoe(self) -> List[str]:
    self.shoe.cards = []

    for _ in range(self.shoe.deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.cards.append(card)

    self.shoe.full_size = 52 * self.shoe.deck_count
    assert self.shoe.full_size == len(self.shoe.cards)

  def to_dict(self):
    return {
      "shoe": self.shoe.to_dict(),
      "hand": [h.to_dict() for h in self.hand]
    }
