from enum import Enum
from typing import List
from entities.Player import Player
from entities.Dealer import Dealer
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from services.ServerLogger import ServerLogger

class GameState(Enum):
  NOT_STARTED = 0
  BETTING = 1
  DEALING = 2
  HUMAN_PLAYER_DECISIONS = 3
  AI_PLAYER_DECISIONS = 4
  DEALER_DECISIONS = 5
  PAYOUTS = 6

class Game:
  dealer: Dealer
  players: List[Player]     # Index 0 will always be the human player
  min_bet: int
  max_bet: int
  shoe_reset_percentage: int
  state: GameState

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

    self.dealer = Dealer()
    self.dealer.load_shoe(deck_count)

    self.min_bet = min_bet
    self.max_bet = max_bet
    self.shoe_reset_percentage = shoe_reset_percentage
    self.state = GameState.NOT_STARTED

  def start(self):
    self.state = GameState.BETTING

  def place_bets(self, bet: int):
    # Human player bet
    self.players[0].place_bet(self.min_bet, self.max_bet, bet)

    # AI bets
    for i in range (1, len(self.players)):
      self.players[i].place_bet(self.min_bet, self.max_bet)

    ServerLogger.debug(0)
    self.deal_cards()
    ServerLogger.debug(5)

  def deal_cards(self):
    ServerLogger.debug(1)
    self.state = GameState.DEALING
    ServerLogger.debug(2)
    self.dealer.deal(self.players, self.shoe_reset_percentage)
    ServerLogger.debug(3)
    self.state = GameState.HUMAN_PLAYER_DECISIONS
    ServerLogger.debug(4)

  def to_dict(self):
    return {
      "state": self.state.name,
      "min_bet": self.min_bet,
      "max_bet": self.max_bet,
      "players": [p.to_dict() for p in self.players],
      "shoe_reset_percentage": self.shoe_reset_percentage
    }
