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
    # TODO: Implement deviation skill level
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
      wants_surrender = self._check_for_surrender(active_player_hand, dealer_face_card_value, true_count)
      if wants_surrender:
        decisions.append(PlayerDecision.SURRENDER)

    if self.__rules_engine.can_split(active_player_hand, len(player_hands)):
      wants_split = self._check_for_split(player_hands, active_player_hand, dealer_face_card_value, true_count)
      if wants_split:
        decisions.append(PlayerDecision.SPLIT)

    adjusted_player_hand_value = self._get_adjusted_player_hand_value(active_player_hand)
    BlackjackLogger.debug(f"\t\tActual hand value: {active_player_hand.get_value()}")
    BlackjackLogger.debug(f"\t\tAdjusted hand value: {adjusted_player_hand_value}")

    if active_player_hand.is_soft():
      decisions.extend(BasicStrategy.soft_totals[(true_count, dealer_face_card_value, adjusted_player_hand_value)])
    else:
      decisions.extend(BasicStrategy.hard_totals[(true_count, dealer_face_card_value, adjusted_player_hand_value)])
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
    adjusted_player_hand_value = self._get_adjusted_player_hand_value(player_hand)
    return BasicStrategy.surrender[(true_count, dealer_face_card_value, adjusted_player_hand_value)]

  def _check_for_surrender(
    self,
    player_hand: Hand,
    dealer_face_card_value: int,
    true_count: int
  ) -> bool:
    adjusted_player_hand_value = self._get_adjusted_player_hand_value(player_hand)
    should_surrender = BasicStrategy.surrender[(true_count, dealer_face_card_value, adjusted_player_hand_value)]
    if should_surrender:
      return True
    return False

  def _check_for_split(
    self,
    player_hands: List[Hand],
    active_player_hand: Hand,
    dealer_face_card_value: int,
    true_count: int
  ):
    splitting_is_allowed = self.__rules_engine.can_split(active_player_hand, len(player_hands))
    if splitting_is_allowed:
      adjusted_player_hand_value = self._get_adjusted_player_hand_value(active_player_hand)
      half_adjusted_player_hand_value = adjusted_player_hand_value // 2
      splitting_decision = BasicStrategy.pair_splitting[
        (true_count, dealer_face_card_value, half_adjusted_player_hand_value)
      ]
      if splitting_decision == PairSplittingDecision.YES:
        return True
      if splitting_decision == PairSplittingDecision.IF_DOUBLE_AFTER_SPLITTING_ALLOWED:
        if self.__rules_engine.can_double_after_split():
          return True
    return False

  # This is a pretty lame way of simulating bad accuracy for "poor skill"
  # bots. Essentially, the bot will intrepret its hand's value incorrectly
  # sometimes and will bet according to that incorrect value
  def _get_adjusted_player_hand_value(self, player_hand: Hand) -> int:
    hand_is_soft = player_hand.is_soft()
    active_player_hand_value = player_hand.get_value()
    accuracy_roll = random.randint(self.__basic_strategy_skill_level, 100)
    BlackjackLogger.debug(f"\t\tAccuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10
    plus_or_minus_roll = random.randint(1, 2)
    if plus_or_minus_roll == 1:
      adjusted_player_hand_value = int(active_player_hand_value + spread)
    else:
      adjusted_player_hand_value = int(active_player_hand_value - spread)

    if adjusted_player_hand_value > 21:
      adjusted_player_hand_value = 21
    elif adjusted_player_hand_value < 4 and not hand_is_soft:
      adjusted_player_hand_value = 4
    elif adjusted_player_hand_value < 12 and hand_is_soft:
      adjusted_player_hand_value = 12

    return adjusted_player_hand_value
