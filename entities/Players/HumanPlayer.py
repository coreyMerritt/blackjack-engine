from typing import List
from entities.Card import Card
from entities.Player import Player
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo


class HumanPlayer(Player):
  def __init__(self, human_player_info: HumanPlayerInfo) -> None:
    self.hands: List[List[Card]] = []
    self.money = human_player_info.money
    self.current_bet = 0
    self.doubled_down = False

  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    self.current_bet = bet
