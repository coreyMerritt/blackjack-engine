import random
from typing import List
from entities.Hand import Hand
from entities.Player import Player
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.BetSpread import BetSpread
from models.enums.Face import Face
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.RulesEngine import RulesEngine


class AiPlayer(Player):
  __basic_strategy_engine: BasicStrategyEngine
  # TODO: This isn't really implemented at all yet -- can't really do so until we implement counting
  __bet_spread: BetSpread

  def __init__(self, ai_player_info: AiPlayerInfo, rules_engine: RulesEngine) -> None:
    super().__init__(ai_player_info)
    self.__basic_strategy_engine = BasicStrategyEngine(ai_player_info.basic_strategy_skill_level, rules_engine)
    self.__bet_spread = ai_player_info.bet_spread

  def get_decisions(self, active_hand: Hand, dealer_facecard_value: int) -> List[PlayerDecision]:
    return self.__basic_strategy_engine.get_play(self.get_hands(), active_hand, dealer_facecard_value)

  def get_insurance_bet(self) -> int:
    # Should we allow other insurance bets?
    return self.get_hands()[0].get_bet() / 2

  def get_bet_spread(self) -> BetSpread:
    return self.__bet_spread

  def determine_bet(self, rules_engine: RulesEngine) -> None:
    return random.randint(rules_engine.get_min_bet(), rules_engine.get_max_bet())

  def wants_insurance(self, dealer_upcard_face: Face) -> bool:
    assert self.get_hand_count() == 1
    return self.__basic_strategy_engine.wants_insurance(self.get_hands(), dealer_upcard_face)

  def wants_to_surrender(self, dealer_face_card_value: int) -> bool:
    assert self.get_hand_count() == 1
    return self.__basic_strategy_engine.wants_to_surrender(dealer_face_card_value, self.get_hand(0))
