import random
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from services.BasicStrategyEngine import BasicStrategyEngine
from services.RulesEngine import RulesEngine


class AiPlayer(Player):
  __basic_strategy_engine: BasicStrategyEngine

  def __init__(self, ai_player_info: AiPlayerInfo, basic_strategy_engine: BasicStrategyEngine) -> None:
    super().__init__(ai_player_info)
    self.__basic_strategy_engine = BasicStrategyEngine(ai_player_info.basic_strategy_skill_level)

  def determine_bet(self, rules_engine: RulesEngine) -> None:
    return random.randint(rules_engine.get_min_bet(), rules_engine.get_max_bet())

  def wants_insurance(self) -> bool:
    assert self.get_hand_count() == 1
