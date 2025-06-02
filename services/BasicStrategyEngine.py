import random
from typing import List
from entities.Hand import Hand
from models.core.BasicStrategy import BasicStrategy
from models.enums.Face import Face
from models.enums.PlayerDecision import PlayerDecision
from models.enums.PairSplittingDecision import PairSplittingDecision
from services.BlackjackLogger import BlackjackLogger
from services.RulesEngine import RulesEngine


class BasicStrategyEngine():
  __basic_strategy_skill_level: int
  __deviations_skill_level: int
  __rules_engine: RulesEngine

  def __init__(
    self,
    basic_strategy_skill_level: int,
    deviations_skill_level: int,
    rules_engine: RulesEngine
  ):
    self.__basic_strategy_skill_level = basic_strategy_skill_level
    self.__deviations_skill_level = deviations_skill_level
    self.__rules_engine = rules_engine

  def get_play(
    self,
    player_hands: List[Hand],
    active_player_hand: Hand,
    dealer_face_card_value: int,
    true_count: int
  ) -> List[PlayerDecision]:
    assert isinstance(dealer_face_card_value, int)
    decisions = []
    if self.__rules_engine.can_late_surrender(active_player_hand):
      wants_surrender = self.__check_for_surrender(active_player_hand, dealer_face_card_value, true_count)
      if wants_surrender:
        decisions.append(PlayerDecision.SURRENDER)

    if self.__rules_engine.can_split(active_player_hand, len(player_hands)):
      wants_split = self.__check_for_split(player_hands, active_player_hand, dealer_face_card_value, true_count)
      if wants_split:
        decisions.append(PlayerDecision.SPLIT)

    adjusted_true_count = self.__get_adjusted_true_count(true_count)
    BlackjackLogger.debug(f"\t\tActual true count: {active_player_hand.get_value()}")
    BlackjackLogger.debug(f"\t\tAdjusted true count: {adjusted_true_count}")

    adjusted_player_hand_value = self.__get_adjusted_player_hand_value(active_player_hand)
    BlackjackLogger.debug(f"\t\tActual hand value: {active_player_hand.get_value()}")
    BlackjackLogger.debug(f"\t\tAdjusted hand value: {adjusted_player_hand_value}")

    if active_player_hand.is_soft():
      decisions.extend(
        BasicStrategy.soft_totals[(adjusted_true_count, dealer_face_card_value, adjusted_player_hand_value)]
      )
    else:
      decisions.extend(
        BasicStrategy.hard_totals[(adjusted_true_count, dealer_face_card_value, adjusted_player_hand_value)]
      )
    return decisions

  # We're proceeding on the assumption that insurance is always bad.
  def wants_insurance(self, hands: List[Hand], dealer_upcard_face: Face) -> bool:
    if not self.__rules_engine.can_insure(hands, dealer_upcard_face):
      return False
    accuracy_roll = random.randint(self.__basic_strategy_skill_level, 100)
    if accuracy_roll > 10:
      return False
    return True

  def wants_to_surrender(self, dealer_face_card_value: int, player_hand: Hand, true_count: int) -> bool:
    if not self.__rules_engine.can_late_surrender(player_hand):
      return False
    adjusted_true_count = self.__get_adjusted_true_count(true_count)
    adjusted_player_hand_value = self.__get_adjusted_player_hand_value(player_hand)
    return BasicStrategy.surrender[(adjusted_true_count, dealer_face_card_value, adjusted_player_hand_value)]

  def __check_for_split(
    self,
    player_hands: List[Hand],
    active_player_hand: Hand,
    dealer_face_card_value: int,
    true_count: int
  ) -> bool:
    splitting_is_allowed = self.__rules_engine.can_split(active_player_hand, len(player_hands))
    if splitting_is_allowed:
      adjusted_true_count = self.__get_adjusted_true_count(true_count)
      adjusted_player_hand_value = self.__get_adjusted_player_hand_value(active_player_hand)
      half_adjusted_player_hand_value = adjusted_player_hand_value // 2
      splitting_decision = BasicStrategy.pair_splitting[
        (adjusted_true_count, dealer_face_card_value, half_adjusted_player_hand_value)
      ]
      if splitting_decision == PairSplittingDecision.YES:
        return True
      if splitting_decision == PairSplittingDecision.IF_DOUBLE_AFTER_SPLITTING_ALLOWED:
        if self.__rules_engine.can_double_after_split():
          return True
    return False

  def __check_for_surrender(
    self,
    player_hand: Hand,
    dealer_face_card_value: int,
    true_count: int
  ) -> bool:
    adjusted_true_count = self.__get_adjusted_true_count(true_count)
    adjusted_player_hand_value = self.__get_adjusted_player_hand_value(player_hand)
    should_surrender = BasicStrategy.surrender[
      (adjusted_true_count, dealer_face_card_value, adjusted_player_hand_value)
    ]
    if should_surrender:
      return True
    return False

  def __get_adjusted_player_hand_value(self, player_hand: Hand) -> int:
    hand_is_soft = player_hand.is_soft()
    player_hand_value = player_hand.get_value()

    if hand_is_soft:
      minimum = 12
    else:
      minimum = 4

    return self.__get_some_adjusted_value(
      self.__basic_strategy_skill_level,
      player_hand_value,
      minimum,
      21
    )

  def __get_adjusted_true_count(self, true_count: int) -> int:
    if true_count is None:
      return None
    return self.__get_some_adjusted_value(
      self.__deviations_skill_level,
      true_count,
      -1,
      6
    )

  def __get_some_adjusted_value(self, skill_level: int, some_val: int, minimum: int, maximum: int) -> int:
    accuracy_roll = random.randint(skill_level, 100)
    BlackjackLogger.debug(f"\t\tAccuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10

    plus_or_minimumus_roll = random.randint(1, 2)
    if plus_or_minimumus_roll == 1:
      adjusted_player_hand_value = int(some_val + spread)
    else:
      adjusted_player_hand_value = int(some_val - spread)

    if adjusted_player_hand_value > maximum:
      adjusted_player_hand_value = maximum
    elif adjusted_player_hand_value < minimum:
      adjusted_player_hand_value = minimum

    return adjusted_player_hand_value
