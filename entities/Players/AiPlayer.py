from math import ceil, floor
from typing import List
from entities.Card import Card
from entities.Hand import Hand
from entities.Player import Player
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.BetSpread import BetSpread
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.BlackjackLogger import BlackjackLogger
from services.CardCountingEngine import CardCountingEngine
from services.RulesEngine import RulesEngine


class AiPlayer(Player):
  __counts_cards: bool
  __plays_deviations: bool
  __running_count: int
  __basic_strategy_engine: BasicStrategyEngine
  __card_counting_engine: CardCountingEngine
  __bet_spread: BetSpread

  def __init__(self, ai_player_info: AiPlayerInfo, rules_engine: RulesEngine):
    super().__init__(ai_player_info)
    self.__counts_cards = ai_player_info.counts_cards
    self.__plays_deviations = ai_player_info.plays_deviations
    self.__running_count = 0
    self.__basic_strategy_engine = BasicStrategyEngine(
      ai_player_info.basic_strategy_skill_level,
      ai_player_info.deviations_skill_level,
      rules_engine
    )
    self.__card_counting_engine = CardCountingEngine(ai_player_info.card_counting_skill_level)
    self.__bet_spread = ai_player_info.bet_spread

  def counts_cards(self) -> bool:
    return self.__counts_cards

  def plays_deviations(self) -> bool:
    return self.__plays_deviations

  def wants_insurance(self, dealer_facecard: Card) -> bool:
    assert self.get_hand_count() == 1
    if self.has_blackjack():
      return False
    return self.__basic_strategy_engine.wants_insurance(self.get_hands(), dealer_facecard.get_face())

  def wants_to_surrender(self, dealer_facecard: Card, decks_remaining: float) -> bool:
    assert self.get_hand_count() == 1
    if self.has_blackjack():
      return False
    hand = self.get_hand(0)
    if hand.is_soft():
      return False
    # This is a practical but imperfect check, since realistically we only surrender
    # on 15/16 anyway, and we want to ensure we don't surrender 8/8
    if hand.is_pair():
      return False
    return self.__basic_strategy_engine.wants_to_surrender(
      dealer_facecard.get_value(),
      hand,
      self.calculate_true_count(decks_remaining)
    )

  def calculate_true_count(self, decks_remaining: float) -> int:
    genuine_true_count = floor(self.get_running_count() / ceil(decks_remaining))
    BlackjackLogger.debug(f"\t\tGenuine true count is: {genuine_true_count}")
    return genuine_true_count

  def get_running_count(self) -> int:
    return self.__running_count

  def update_running_count(self, card_value: int) -> None:
    if self.counts_cards():
      count_adjustment = self.__card_counting_engine.get_count_adjustment(card_value)
      self.__running_count += count_adjustment
    BlackjackLogger.debug(f"\t\t\tRunning count is: {self.get_running_count()}")

  def get_bet_spread(self) -> BetSpread:
    return self.__bet_spread

  def get_decisions(self, active_hand: Hand, dealer_facecard_value: int, decks_remaining: int) -> List[PlayerDecision]:
    if self.counts_cards() and self.plays_deviations():
      true_count = self.calculate_true_count(decks_remaining)
    else:
      true_count = None
    decisions = self.__basic_strategy_engine.get_play(
      self.get_hands(),
      active_hand,
      dealer_facecard_value,
      true_count
    )
    BlackjackLogger.debug(f"\t\tWants: {[d.name for d in decisions]}")
    return decisions

  def get_insurance_bet(self) -> int:
    return self.get_hands()[0].get_insurance_bet()

  def set_running_count(self, running_count: int) -> None:
    self.__running_count = running_count

  def reset_running_count(self) -> None:
    self.__running_count = 0

  def calculate_bet(self, rules_engine: RulesEngine, decks_remaining: int) -> None:
    true_count = self.calculate_true_count(decks_remaining)
    min_bet = rules_engine.get_min_bet()
    max_bet = rules_engine.get_max_bet()
    bet_spread = self.get_bet_spread()

    if true_count == 1:
      bet = bet_spread.true_one
    elif true_count == 2:
      bet = bet_spread.true_two
    elif true_count == 3:
      bet = bet_spread.true_three
    elif true_count == 4:
      bet = bet_spread.true_four
    elif true_count == 5:
      bet = bet_spread.true_five
    elif true_count >= 6:
      bet = bet_spread.true_six
    else:
      bet = bet_spread.true_zero

    if bet > self.get_bankroll():
      bet = self.get_bankroll()

    if bet < min_bet:
      bet = min_bet
    if bet > max_bet:
      bet = max_bet

    assert rules_engine.bet_is_legal(bet)
    return bet
