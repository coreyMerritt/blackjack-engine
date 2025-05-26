from entities.Player import Player
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo


class HumanPlayer(Player):
  def __init__(self, human_player_info: HumanPlayerInfo) -> None:
    self._hands = []
    self._money = human_player_info.money
    self._current_bet = 0
    self._doubled_down = False

  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    self._current_bet = bet
