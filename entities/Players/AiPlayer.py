import random
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.GameRules import GameRules


class AiPlayer(Player):
  _basic_strategy_skill_level: int

  def __init__(self, ai_player_info: AiPlayerInfo) -> None:
    self._hands = []
    self._money = ai_player_info.money
    self._current_bet = 0
    self._doubled_down = False
    self._basic_strategy_skill_level = ai_player_info.basic_strategy_skill_level

  def place_bet(self, bet: int | None, rules: GameRules) -> None:
    if bet is not None:
      self._current_bet = bet
      return

    random_bet = random.randint(rules.min_bet, rules.max_bet)
    self._current_bet = random_bet
