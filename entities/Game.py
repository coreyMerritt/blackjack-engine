from enum import Enum
from typing import List
from entities.Player import Player
from entities.Dealer import Dealer
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer

class GameState(Enum):
  NOT_STARTED = 0
  BETTING = 1
  DEALING = 2
  HUMAN_PLAYER_DECISIONS = 3
  AI_PLAYER_DECISIONS = 4
  DEALER_DECISIONS = 5
  PAYOUTS = 6

class Game:
  min_bet: int
  max_bet: int
  state: GameState
  dealer: Dealer
  players: List[Player]     # Index 0 will always be the human player

  def __init__(
    self,
    deck_count,
    ai_player_count,
    min_bet,
    max_bet,
    shoe_reset_percentage
  ):
    self.players = []
    self.players.append(HumanPlayer())

    for _ in range(ai_player_count):
      ai_player = AiPlayer()
      self.players.append(ai_player)

    self.dealer = Dealer(deck_count)
    self.dealer.load_shoe()
    self.dealer.shuffle_shoe()

    self.min_bet = min_bet
    self.max_bet = max_bet
    self.dealer.shoe.reset_percentage = shoe_reset_percentage
    self.state = GameState.NOT_STARTED

  def place_bets(self, bet: int):
    # Human player bet
    self.players[0].place_bet(self.min_bet, self.max_bet, bet)

    # AI bets
    for i in range (1, len(self.players)):
      self.players[i].place_bet(self.min_bet, self.max_bet)

  def deal_cards(self):
    full_shoe = self.dealer.shoe.full_size
    shoe_is_above_reset_point = len(self.dealer.shoe.cards) > (full_shoe / (100 / self.dealer.shoe.reset_percentage))
    if not shoe_is_above_reset_point:
      self.dealer.load_shoe()
      self.dealer.shuffle_shoe()
    self.dealer.deal(self.players)

  def to_dict(self):
    return {
      "max_bet": self.max_bet,
      "min_bet": self.min_bet,
      "state": self.state.name,
      "dealer": self.dealer.to_dict(),
      "players": [p.to_dict() for p in self.players]
    }
