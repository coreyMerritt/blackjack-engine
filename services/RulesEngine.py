from typing import List
from entities.Hand import Hand
from entities.Player import Player
from entities.Shoe import Shoe
from models.core.rules.BettingRules import BettingRules
from models.core.rules.DealerRules import DealerRules
from models.core.rules.DoubleDownRules import DoubleDownRules
from models.core.rules.GameRules import GameRules
from models.core.rules.SplittingRules import SplittingRules
from models.core.rules.SurrenderRules import SurrenderRules
from models.enums.Face import Face
from models.enums.GameState import GameState
from models.enums.PlayerDecision import PlayerDecision


class RulesEngine():
  __betting_rules: BettingRules
  __dealer_rules: DealerRules
  __double_down_rules: DoubleDownRules
  __splitting_rules: SplittingRules
  __surrender_rules: SurrenderRules

  def __init__(self, rules: GameRules):
    self.__betting_rules = rules.betting_rules
    self.__dealer_rules = rules.dealer_rules
    self.__double_down_rules = rules.double_down_rules
    self.__splitting_rules = rules.splitting_rules
    self.__surrender_rules = rules.surrender_rules

  def is_legal_play(
    self,
    decision: PlayerDecision,
    player: Player,
    state: GameState
  ) -> bool:
    if state != GameState.HUMAN_PLAYER_DECISIONS and state != GameState.AI_PLAYER_DECISIONS:
      return False
    active_hand = player.calculate_active_hand()
    current_hand_count = player.get_hand_count()
    match decision:
      case PlayerDecision.HIT:
        return self.__can_hit(active_hand)
      case PlayerDecision.STAND:
        return True
      case PlayerDecision.DOUBLE_DOWN:
        if player.get_bankroll() > active_hand.get_bet():
          return self.__can_double_down(active_hand)
        return False
      case PlayerDecision.SPLIT:
        if player.get_bankroll() > active_hand.get_bet():
          return self.can_split(active_hand, current_hand_count)
        return False
      case PlayerDecision.SURRENDER:
        return False
      case _:
        raise ValueError(f"PlayerDecision not implemented: {decision.value}")

  def get_min_bet(self) -> int:
    return self.__betting_rules.min_bet

  def get_max_bet(self) -> int:
    return self.__betting_rules.max_bet

  def bet_is_legal(self, bet: int) -> bool:
    if bet >= self.__betting_rules.min_bet and bet <= self.__betting_rules.max_bet:
      return True
    return False

  def can_double_after_split(self) -> bool:
    if self.__double_down_rules.double_after_split_including_aces:
      return True
    if self.__double_down_rules.double_after_split_except_aces:
      return True
    return False

  def can_early_surrender(self, hand: Hand) -> bool:
    if not self.__surrender_rules.early_surrender_allowed:
      return False
    if hand.get_card_count() != 2:
      return False
    if hand.is_from_split():
      return False
    if hand.is_doubled_down():
      return False
    return True

  def can_late_surrender(self, hand: Hand) -> bool:
    if not self.__surrender_rules.late_surrender_allowed:
      return False
    if hand.get_card_count() != 2:
      return False
    if hand.is_from_split():
      return False
    if hand.is_doubled_down():
      return False
    return True

  def can_insure(self, hands: List[Hand], dealer_facecard_face: Face) -> bool:
    if len(hands) > 1:
      return False
    if dealer_facecard_face != Face.ACE:
      return False
    if hands[0].get_insurance_bet() > 0:
      return False
    return True

  def can_split(self, hand: Hand, current_hand_count: int) -> bool:
    max_hands_allowed = self.__splitting_rules.maximum_hand_count
    if current_hand_count == max_hands_allowed:
      return False
    if hand.is_finalized():
      return False
    if hand.get_card_count() == 2:
      if hand.is_pair():
        return True
      if hand.get_card_face(0) == hand.get_card_face(1):
        return True
    return False

  def dealer_hits_soft_seventeen(self) -> bool:
    return self.__dealer_rules.dealer_hits_soft_seventeen

  def shoe_must_be_shuffled(self, shoe: Shoe) -> bool:
    card_shuffle_point = (self.__dealer_rules.deck_count * 52) * (self.__dealer_rules.shoe_reset_percentage / 100)
    if shoe.get_card_count() <= card_shuffle_point:
      return True
    return False

  # This whole function is pretty ugly, probably its a sign that I should
  # rewrite the DoubleDownRules model, but I'm choosing violence today
  def __can_double_down(self, hand: Hand) -> bool:
    hand_value = hand.get_value()
    hand_card_count = hand.get_card_count()
    hand_is_from_split = hand.is_from_split()
    hand_first_card_face = hand.get_card_face(0)

    # General rules
    if not self.__double_down_rules.double_after_hit:
      if hand_card_count > 2:
        return False

    # Split-based rules
    if self.__double_down_rules.double_after_split_except_aces:
      if not self.__double_down_rules.double_after_split_including_aces:
        if hand_is_from_split and hand_first_card_face == Face.ACE:
          return False
    else:
      if not self.__double_down_rules.double_after_split_including_aces:
        if hand_is_from_split:
          return False

    # Value-based rules
    if not self.__double_down_rules.double_on_any_two_cards:
      if self.__double_down_rules.double_on_nine_ten_eleven_only:
        if self.__double_down_rules.double_on_ten_eleven_only:
          if hand_value != 9 and hand_value != 10 and hand_value != 11:
            return False
        else:
          if hand_value != 9 and hand_value != 10 and hand_value != 11:
            return False
      else:
        if self.__double_down_rules.double_on_ten_eleven_only:
          if hand_value != 10 and hand_value != 11:
            return False
        else:
          return False
    return True

  def __can_hit(self, hand: Hand) -> bool:
    if hand.get_value() >= 21:
      return False
    if not self.__splitting_rules.can_hit_aces:
      if hand.is_from_split():
        if hand.get_card_face(0) == Face.ACE:
          return False
    return True
