import random
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.GameRules import GameRules


class AiPlayer(Player):
  _basic_strategy_skill_level: int

  def __init__(self, ai_player_info: AiPlayerInfo) -> None:
    super().__init__(ai_player_info)
    self._basic_strategy_skill_level = ai_player_info.basic_strategy_skill_level

  def determine_bet(self, rules: GameRules) -> None:
    return random.randint(rules.min_bet, rules.max_bet)
