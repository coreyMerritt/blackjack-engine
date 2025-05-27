import random
from typing import List
from entities.Hand import Hand
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from models.enums.Face import Face
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.RulesEngine import RulesEngine


class AiPlayer(Player):
  __basic_strategy_engine: BasicStrategyEngine

  def __init__(self, ai_player_info: AiPlayerInfo, rules_engine: RulesEngine) -> None:
    super().__init__(ai_player_info)
    self.__basic_strategy_engine = BasicStrategyEngine(ai_player_info.basic_strategy_skill_level, rules_engine)

  def get_decisions(self, active_hand: Hand, dealer_upcard_face: Face) -> List[PlayerDecision]:
    self.__basic_strategy_engine.get_play(
      active_hand,
      dealer_upcard_face,
      True,   # TODO: Implement
      False   # TODO: Implement
    )

  def get_insurance_bet(self) -> int:
    # TODO: Should we allow other insurance bets?
    return self.get_hands()[0].get_bet() / 2

  def determine_bet(self, rules_engine: RulesEngine) -> None:
    return random.randint(rules_engine.get_min_bet(), rules_engine.get_max_bet())

  def wants_insurance(self) -> bool:
    assert self.get_hand_count() == 1
    return self.__basic_strategy_engine.wants_insurance
