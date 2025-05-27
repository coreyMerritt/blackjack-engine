from typing import List
from entities.Hand import Hand
from entities.Shoe import Shoe
from models.core.BettingRules import BettingRules
from models.core.DealerRules import DealerRules
from models.core.DoubleDownRules import DoubleDownRules
from models.core.GameRules import GameRules
from models.core.SplittingRules import SplittingRules
from models.enums.Face import Face


class RulesEngine():
  __betting_rules: BettingRules
  __dealer_rules: DealerRules
  __double_down_rules: DoubleDownRules
  __splitting_rules: SplittingRules

  def __init__(self, rules: GameRules):
    self.__betting_rules = rules.betting_rules
    self.__dealer_rules = rules.dealer_rules
    self.__double_down_rules = rules.double_down_rules
    self.__splitting_rules = rules.splitting_rules

  def get_min_bet(self) -> int:
    return self.__betting_rules.min_bet

  def get_max_bet(self) -> int:
    return self.__betting_rules.max_bet

  def bet_is_legal(self, bet) -> bool:
    if bet >= self.__betting_rules.min_bet and bet <= self.__betting_rules.max_bet:
      return True
    return False

  def dealer_hits_soft_seventeen(self) -> bool:
    return self.__dealer_rules.dealer_hits_soft_seventeen

  def shoe_must_be_shuffled(self, shoe: Shoe) -> bool:
    card_shuffle_point = (self.__dealer_rules.deck_count * 52) * self.__dealer_rules.shoe_reset_percentage
    if shoe.get_card_count() <= card_shuffle_point:
      return True
    return False

  def can_double_down(self, hand: Hand) -> bool:
    hand_value = hand.get_value()
    hand_card_count = hand.get_card_count()
    hand_is_from_split = hand.is_from_split()
    hand_first_card_face = hand.get_card_face(0)

    if not self.__double_down_rules.double_after_hit:
      if hand_card_count > 2:
        return False
    if not self.__double_down_rules.double_after_split_including_aces:
      if not self.__double_down_rules.double_after_split_except_aces:
        if hand_is_from_split:
          return False
      if hand_is_from_split and hand_first_card_face == Face.ACE:
        return False
    if not self.__double_down_rules.double_on_any_two_cards:
      if not self.__double_down_rules.double_on_nine_ten_eleven_only:
        if not self.__double_down_rules.double_on_ten_eleven_only:
          return False
        if hand_value != 10 and hand_value != 11:
          return False
      if hand_value != 9 and hand_value != 10 and hand_value != 11:
        return False
    return True

  def can_split(self, hands: List[Hand]) -> bool:
    max_hands_allowed = self.__splitting_rules.maximum_hand_count
    current_hand_count = len(hands)
    if current_hand_count == max_hands_allowed:
      return False
    for hand in hands:
      if hand.is_finalized():
        continue
      if hand.get_card_count() == 2:
        if hand.get_card_value(0) == hand.get_card_value(1):
          return True
    return False
