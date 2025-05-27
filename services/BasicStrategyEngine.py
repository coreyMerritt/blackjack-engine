import random
from typing import List
from entities.Card import Card
from models.core.BasicStrategy import BasicStrategy
from models.enums.PlayerDecision import PlayerDecision
from models.enums.PairSplittingDecision import PairSplittingDecision
from services.BlackjackLogger import BlackjackLogger


class BasicStrategyEngine():
  __skill_level: int

  def __init__(self, skill_level: int):
    self.__skill_level = skill_level

  def get_play(
    self,
    player_hand: List[Card],
    dealer_face_card_value: int,
    double_after_splitting_allowed: bool,
    is_from_split: bool
  ) -> PlayerDecision:
    surrender = self._check_for_surrender(
      player_hand,
      dealer_face_card_value
    )
    if surrender:
      return PlayerDecision.SURRENDER

    split = self._check_for_split(
      player_hand,
      dealer_face_card_value,
      is_from_split,
      double_after_splitting_allowed
    )
    if split:
      return PlayerDecision.SPLIT

    is_soft = False
    player_hand_value = 0
    for card in player_hand:
      player_hand_value += card.get_value()
      if card.value_can_reset():
        is_soft = True

    accuracy_roll = random.randint(self.__skill_level, 100)
    BlackjackLogger.debug(f"Accuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10
    plus_or_minus_roll = random.randint(1, 2)
    if plus_or_minus_roll == 1:
      drunken_player_hand_value = int(player_hand_value + spread)
    else:
      drunken_player_hand_value = int(player_hand_value - spread)

    if drunken_player_hand_value > 21:
      drunken_player_hand_value = 21
    elif drunken_player_hand_value < 4 and not is_soft:
      drunken_player_hand_value = 4
    elif drunken_player_hand_value < 13 and is_soft:
      drunken_player_hand_value = 13
    BlackjackLogger.debug(f"100% Acc: {drunken_player_hand_value == player_hand_value}")
    BlackjackLogger.debug(f"Dealer is showing: {dealer_face_card_value}")

    if is_soft:
      player_decision = BasicStrategy.soft_totals[(dealer_face_card_value, drunken_player_hand_value)]
    else:
      player_decision = BasicStrategy.hard_totals[(dealer_face_card_value, drunken_player_hand_value)]
    return player_decision

  def _check_for_surrender(
    self,
    player_hand: List[Card],
    dealer_face_card_value: int
  ) -> bool:

    player_hand_value = 0
    for card in player_hand:
      player_hand_value += card.get_value()

    accuracy_roll = random.randint(self.__skill_level, 100)
    BlackjackLogger.debug(f"Surrender accuracy roll: {accuracy_roll}")
    spread = (100 - accuracy_roll) / 10
    plus_or_minus_roll = random.randint(1, 2)
    if plus_or_minus_roll == 1:
      drunken_player_hand_value = int(player_hand_value + spread)
    else:
      drunken_player_hand_value = int(player_hand_value - spread)

    should_surrender = BasicStrategy.surrender[(dealer_face_card_value, drunken_player_hand_value)]
    if should_surrender:
      return True
    return False

  def _check_for_split(
    self,
    player_hand: List[Card],
    dealer_face_card_value: int,
    is_from_split: bool,
    double_after_splitting_allowed: bool
  ):
    cards_match = (player_hand[0].get_value() == player_hand[1].get_value()) and len(player_hand) == 2
    splitting_is_allowed = cards_match and (not is_from_split or double_after_splitting_allowed)
    if splitting_is_allowed:
      accuracy_roll = random.randint(self.__skill_level, 100)
      BlackjackLogger.debug(f"Surrender accuracy roll: {accuracy_roll}")
      spread = (100 - accuracy_roll) / 10
      plus_or_minus_roll = random.randint(1, 2)
      if plus_or_minus_roll == 1:
        drunken_player_hand_value = int(player_hand[0].get_value() + spread)
      else:
        drunken_player_hand_value = int(player_hand[0].get_value() - spread)

      splitting_decision = BasicStrategy.pair_splitting[(dealer_face_card_value, drunken_player_hand_value)]
      if splitting_decision == PairSplittingDecision.YES:
        return True
      if (
        splitting_decision == PairSplittingDecision.IF_DOUBLE_AFTER_SPLITTING_ALLOWED
        and double_after_splitting_allowed
      ):
        return True

    return False
