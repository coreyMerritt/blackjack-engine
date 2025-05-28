import random
from typing import List
from entities.Hand import Hand
from models.core.BasicStrategy import BasicStrategy
from models.enums.PlayerDecision import PlayerDecision
from models.enums.PairSplittingDecision import PairSplittingDecision
from services.BlackjackLogger import BlackjackLogger
from services.RulesEngine import RulesEngine


class BasicStrategyEngine():
  __skill_level: int
  __rules_engine: RulesEngine

  def __init__(self, skill_level: int, rules_engine: RulesEngine):
    self.__skill_level = skill_level
    self.__rules_engine = rules_engine

  def get_play(
    self,
    player_hands: List[Hand],
    active_player_hand: Hand,
    dealer_face_card_value: int
  ) -> List[PlayerDecision]:
    if self.__rules_engine.can_late_surrender():
      wants_surrender = self._check_for_surrender(active_player_hand, dealer_face_card_value)
      if wants_surrender:
        return [PlayerDecision.SURRENDER]

    if self.__rules_engine.can_split():
      wants_split = self._check_for_split(player_hands, active_player_hand, dealer_face_card_value)
      if wants_split:
        return [PlayerDecision.SPLIT]

    hand_is_soft = active_player_hand.is_soft()
    active_player_hand_value = active_player_hand.get_value()
    accuracy_roll = random.randint(self.__skill_level, 100)
    BlackjackLogger.debug(f"Accuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10
    plus_or_minus_roll = random.randint(1, 2)
    if plus_or_minus_roll == 1:
      drunken_player_hand_value = int(active_player_hand_value + spread)
    else:
      drunken_player_hand_value = int(active_player_hand_value - spread)

    if drunken_player_hand_value > 21:
      drunken_player_hand_value = 21
    elif drunken_player_hand_value < 4 and not hand_is_soft:
      drunken_player_hand_value = 4
    elif drunken_player_hand_value < 13 and hand_is_soft:
      drunken_player_hand_value = 13

    if hand_is_soft:
      player_decision = BasicStrategy.soft_totals[(dealer_face_card_value, drunken_player_hand_value)]
    else:
      player_decision = BasicStrategy.hard_totals[(dealer_face_card_value, drunken_player_hand_value)]
    return player_decision

  # We're proceeding on the assumption that insurance is always bad.
  def wants_insurance(self) -> bool:
    if not self.__rules_engine.can_insure():
      return False
    accuracy_roll = random.randint(self.__skill_level, 100)
    if accuracy_roll > 10:
      return False
    return True

  def wants_to_surrender(self, dealer_face_card_value: int, player_hand_value: int) -> bool:
    if not self.__rules_engine.can_late_surrender():
      return False
    drunken_player_hand_value = self._get_drunken_player_hand_value(player_hand_value)
    return BasicStrategy.surrender[(dealer_face_card_value, drunken_player_hand_value)]

  def _check_for_surrender(
    self,
    player_hand: Hand,
    dealer_face_card_value: int
  ) -> bool:
    drunken_player_hand_value = self._get_drunken_player_hand_value(player_hand.get_value())
    should_surrender = BasicStrategy.surrender[(dealer_face_card_value, drunken_player_hand_value)]
    if should_surrender:
      return True
    return False

  def _check_for_split(
    self,
    player_hands: List[Hand],
    active_player_hand: Hand,
    dealer_face_card_value: int
  ):
    splitting_is_allowed = self.__rules_engine.can_split(player_hands)
    if splitting_is_allowed:
      drunken_player_hand_value = self._get_drunken_player_hand_value(active_player_hand.get_value())
      splitting_decision = BasicStrategy.pair_splitting[(dealer_face_card_value, drunken_player_hand_value)]
      if splitting_decision == PairSplittingDecision.YES:
        return True
      if (
        splitting_decision == PairSplittingDecision.IF_DOUBLE_AFTER_SPLITTING_ALLOWED
        and self.__rules_engine.can_double_after_split()
      ):
        return True

    return False

  # This is a pretty lame way of simulating bad accuracy for "poor skill"
  # bots. Essentially, the bot will intrepret its hand's value incorrectly
  # sometimes and will bet according to that incorrect value
  def _get_drunken_player_hand_value(self, player_hand_value: int) -> int:
    accuracy_roll = random.randint(self.__skill_level, 100)
    BlackjackLogger.debug(f"Surrender accuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10
    plus_or_minus_roll = random.randint(1, 2)
    if plus_or_minus_roll == 1:
      drunken_player_hand_value = int(player_hand_value + spread)
    else:
      drunken_player_hand_value = int(player_hand_value - spread)
    return drunken_player_hand_value
