import random
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from services.RulesEngine import RulesEngine


class AiPlayer(Player):
  __basic_strategy_skill_level: int

  def __init__(self, ai_player_info: AiPlayerInfo) -> None:
    super().__init__(ai_player_info)
    self.__basic_strategy_skill_level = ai_player_info.basic_strategy_skill_level

  def get_basic_strategy_skill_level(self) -> int:
    return self.__basic_strategy_skill_level

  def determine_bet(self, rules_engine: RulesEngine) -> None:
    return random.randint(rules_engine.get_min_bet(), rules_engine.get_max_bet())
