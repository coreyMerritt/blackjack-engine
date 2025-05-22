from typing import List
from entities.Player import Player
from entities.Card import Card, Face, Suit

class Dealer:
  shoe: List[Card]
  full_shoe_size: int
  hand: List[Card]

  def __init__(self):
    self.shoe = []
    self.hand = []

  def load_shoe(self, deck_count: int) -> List[str]:
    for _ in range(deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.append(card)
    self.full_shoe_size = 52 * deck_count

  def deal(self, players: List[Player]):
    for player in players:
      for _ in range(2):
        if len(self.shoe) > (self.full_shoe_size / 5):    # TODO: Un-hardcode this 20% value
          player.hand.append(self.shoe.pop())

    # TODO: This is mostly debugging, shouldnt need a return here
    return_obj = {}
    for i, player in enumerate(players):
      return_obj[i] = player.hand
    return return_obj
