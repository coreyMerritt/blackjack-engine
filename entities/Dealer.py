from random import shuffle
from typing import List
from services.ServerLogger import ServerLogger
from entities.Player import PlayerDecisions
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
    for _ in range(2):
      self.hand.append(self.shoe.cards.pop())

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

  def hit(self, player: Player):
    player.hand.append(self.shoe.cards.pop())

  def handle_ai_decisions(self, ai_players: List[Player]):
    for ai_player in ai_players:
      decision = PlayerDecisions.PLACEHOLDER
      while decision != PlayerDecisions.STAND:
        decision = ai_player.get_decision()
        match decision:
          case PlayerDecisions.HIT:
            ai_player.hand.append(self.shoe.cards.pop())

  def handle_dealer_decisions(self):
    decision = PlayerDecisions.PLACEHOLDER
    while decision != PlayerDecisions.STAND:
      decision = self.get_decision()
      match decision:
        case PlayerDecisions.HIT:
          self.hand.append(self.shoe.cards.pop())

  def get_decision(self):
    if self.get_hand_value() >= 17:
      return PlayerDecisions.STAND
    else:
      return PlayerDecisions.HIT

  def get_hand_value(self):
    value = 0
    for card in self.hand:
      value += card.value

    return value

  def to_dict(self):
    return {
      "shoe": self.shoe.to_dict(),
      "hand": [h.to_dict() for h in self.hand]
    }
