from typing import List
from entities.Player import Player
from entities.Dealer import Dealer
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.api.PlayerInfo import PlayerInfo
from models.enums.GameState import GameState

class Game:
  min_bet: int
  max_bet: int
  state: GameState
  dealer: Dealer
  players: List[Player]     # Index 0 will always be the human player

  def __init__(
    self,
    deck_count: int,
    ai_player_count: int,
    min_bet: int,
    max_bet: int,
    shoe_reset_percentage: int,
    player_info: PlayerInfo
  ):
    self.players = []
    self.players.append(HumanPlayer(player_info))

    for _ in range(ai_player_count):
      ai_player = AiPlayer(player_info)   # TODO: AI players should probably get their own info
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
