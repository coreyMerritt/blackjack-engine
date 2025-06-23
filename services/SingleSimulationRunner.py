import asyncio
from math import inf
import os
import time
from typing import List
from entities.Game import Game
from entities.Hand import Hand
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds
from models.core.results.BankrollResults import BankrollResults
from models.core.results.HandResults import HandResults
from models.core.results.HandResultsCounts import HandResultsCounts
from models.core.results.HandResultsPercentages import HandResultsPercentages
from models.core.results.SimulationSingleResults import SimulationSingleResults
from models.core.results.TimeResults import TimeResults
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult
from services.BlackjackLogger import BlackjackLogger
from services.DatabaseHandler import DatabaseHandler
import services.MathHelper as MathHelper


class SingleSimulationRunner():
  __original_req: CreateSingleSimReq
  __yield_every_x_hands: int
  __bankroll_goal: float
  __bankroll_fail: float
  __human_time_limit: int | None
  __sim_time_limit: int | None
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __results_progress: int
  __start_time: float | None
  __game: Game
  __results: SimulationSingleResults | None
  __database_handler: DatabaseHandler

  def __init__(self, game: Game, bounds: SingleSimBounds, human_time: HumanTime, original_req: CreateSingleSimReq):
    self.__original_req = original_req
    self.__yield_every_x_hands = int(os.getenv("BJE_YIELD_EVERY_X_HANDS", "100"))
    if bounds.bankroll_goal is None:
      self.__bankroll_goal = inf
    else:
      self.__bankroll_goal = bounds.bankroll_goal
    if bounds.bankroll_fail is None:
      self.__bankroll_fail = 0
    else:
      self.__bankroll_fail = bounds.bankroll_fail
    self.__human_time_limit = bounds.human_time_limit
    self.__sim_time_limit = bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__results_progress = 0
    self.__game = game
    self.__results = None
    self.__database_handler = DatabaseHandler()

  async def run(self, called_from_multi=False) -> None:
    if not called_from_multi:
      self.__full_reset()
    self.__start_time = time.time()
    br = self.__game.get_ai_players()[0].get_bankroll()
    bankroll = BankrollResults.model_construct(
      starting=br,
      highest=br
    )
    counts = HandResultsCounts.model_validate({})
    someone_has_bankroll = self.__game.someone_has_bankroll()
    bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()
    bankroll_is_above_fail = self.__calculate_if_bankroll_is_above_fail()
    assert self.get_bankroll_goal() > bankroll.starting
    assert self.get_bankroll_fail() < bankroll.starting

    while(someone_has_bankroll and bankroll_is_below_goal and bankroll_is_above_fail):
      await self.__play_a_hand(bankroll, counts)
      assert self.__results_progress <= 100
      assert self.__results_progress >= -100
      if self.__results_progress == 100 or self.__results_progress == -100:
        break
      someone_has_bankroll = self.__game.someone_has_bankroll()
      bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()
      bankroll_is_above_fail = self.__calculate_if_bankroll_is_above_fail()

    bankroll.ending = self.__game.get_ai_players()[0].get_bankroll()
    assert bankroll.ending >= 0
    max_possible_win = self.__game.get_ai_players()[0].get_bet_spread().true_six * 8
    assert bankroll.ending <= self.__bankroll_goal + max_possible_win
    bankroll.total_profit = bankroll.ending - bankroll.starting
    percentages = HandResultsPercentages.model_construct(
      blackjack=self.__get_blackjack_rate(counts),
      won=self.__get_win_rate(counts),
      drawn=self.__get_draw_rate(counts),
      lost=self.__get_loss_rate(counts),
      surrendered=self.__get_surrender_rate(counts)
    )
    assert sum(percentages.model_dump().values()) >= 99.99
    assert sum(percentages.model_dump().values()) <= 100.01

    won = self.__get_game_result(bankroll.ending)
    r_hands = HandResults.model_construct(
      counts=counts,
      percentages=percentages
    )
    bankroll.profit_per_hand = bankroll.total_profit / counts.total
    bankroll.profit_per_hour = (bankroll.total_profit / counts.total) * self.__hands_per_hour
    r_time = TimeResults.model_construct(
      human_time=self.__get_human_time(counts.total),
      simulation_time= time.time() - self.__start_time
    )
    self.__results = SimulationSingleResults.model_construct(
      won=won,
      hands=r_hands,
      bankroll=bankroll,
      time=r_time
    )
    self.__database_handler.store_simulation_single_result(self.__results, self.__original_req)

  def get_hours_per_day(self) -> int:
    return self.__hours_per_day

  def get_days_per_week(self) -> int:
    return self.__days_per_week

  def get_bankroll_goal(self) -> float:
    return self.__bankroll_goal

  def get_bankroll_fail(self) -> float:
    return self.__bankroll_fail

  def get_bankroll(self) -> float:
    return self.__game.get_ai_players()[0].get_bankroll()

  def get_results_progress(self) -> int:
    return self.__results_progress

  def get_results(self) -> SimulationSingleResults | None:
    if self.__results is None:
      return None
    return self.__results

  def set_results(self, results: SimulationSingleResults) -> None:
    self.__results = results

  def reset_game(self) -> None:
    self.__game.reset_game()

  def __calculate_if_bankroll_is_below_goal(self) -> bool:
    if self.__bankroll_goal:
      return self.__game.get_ai_players()[0].get_bankroll() < self.__bankroll_goal
    else:
      return True

  def __calculate_if_bankroll_is_above_fail(self) -> bool:
    bankroll = self.__game.get_ai_players()[0].get_bankroll()
    return bankroll > self.__bankroll_fail

  def __get_human_time(self, total_hands_played: int) -> float:
    return MathHelper.get_human_time(total_hands_played, self.__hands_per_hour)

  def __get_blackjack_rate(self, counts: HandResultsCounts) -> float:
    return MathHelper.get_percentage(counts.blackjack, counts.total)

  def __get_win_rate(self, counts: HandResultsCounts) -> float:
    return MathHelper.get_percentage(counts.won, counts.total)

  def __get_draw_rate(self, counts: HandResultsCounts) -> float:
    return MathHelper.get_percentage(counts.drawn, counts.total)

  def __get_loss_rate(self, counts: HandResultsCounts) -> float:
    return MathHelper.get_percentage(counts.lost, counts.total)

  def __get_surrender_rate(self, counts: HandResultsCounts) -> float:
    return MathHelper.get_percentage(counts.surrendered, counts.total)

  def __get_game_result(self, ending_bankroll: float) -> bool | None:
    if ending_bankroll <= self.__bankroll_fail:
      return False
    elif ending_bankroll >= self.__bankroll_goal:
      return True
    else:
      return None

  def __full_reset(self) -> None:
    self.__game.reset_game()
    self.__results_progress = 0
    self.__results = None

  async def __play_a_hand(self, bankroll: BankrollResults, counts: HandResultsCounts) -> None:
    if self.__start_time is None:
      raise RuntimeError("Start time wasn't logged.")
    ai_player = self.__game.get_ai_players()[0]
    true_count = ai_player.calculate_true_count(self.__game.get_dealer().get_decks_remaining())
    self.__game.continue_until_state(GameState.CLEANUP)
    assert self.__game.get_state() == GameState.CLEANUP
    self.__update_bankroll(bankroll)
    for hand in ai_player.get_hands():
      self.__update_profits(hand, true_count, bankroll.profit_from_true, counts)
    total_profit = ai_player.get_bankroll() - bankroll.starting
    total_from_true = sum(bankroll.profit_from_true)
    assert abs(total_profit - total_from_true) < 0.01
    self.__game.finish_round()
    assert self.__game.get_state() == GameState.BETTING
    await self.__occasionally_yield_event_loop_control(counts.total)
    self.__update_results_progress(counts.total, time.time() - self.__start_time)

  async def __occasionally_yield_event_loop_control(self, total_hands_played) -> None:
    if total_hands_played % self.__yield_every_x_hands == 0:
      await asyncio.sleep(0)

  def __update_bankroll(self, bankroll: BankrollResults) -> None:
    current_player_bankroll = self.__game.get_ai_players()[0].get_bankroll()
    if bankroll.peak < current_player_bankroll:
      bankroll.peak = current_player_bankroll

  def __update_profits(
    self,
    hand: Hand,
    true_count: int,
    profit_from_true: List[float],
    counts: HandResultsCounts
  ) -> None:
    hand_result = hand.get_result()
    assert hand_result != HandResult.UNDETERMINED
    bet = hand.get_bet()
    assert bet > 0
    payout = hand.get_payout()
    if true_count > 6:
      adjusted_true_count = 6
    elif true_count < 0:
      adjusted_true_count = 0
    else:
      adjusted_true_count = true_count
    profit_from_true[adjusted_true_count] += payout
    if hand_result == HandResult.BLACKJACK:
      counts.blackjack += 1
    elif hand_result == HandResult.WIN:
      counts.won += 1
    elif hand_result == HandResult.LOSS:
      profit_from_true[adjusted_true_count] -= bet
      counts.lost += 1
    elif hand_result == HandResult.DRAW:
      counts.drawn += 1
    elif hand_result == HandResult.SURRENDERED:
      profit_from_true[adjusted_true_count] -= bet / 2
      counts.surrendered += 1
    counts.total += 1
    BlackjackLogger.debug(f"\t\tHand result: {hand_result}")
    BlackjackLogger.debug(f"\t\tPayout: {payout}")

  def __update_results_progress(self, total_hands_played: int, time_elapsed_seconds: float) -> None:
    # if self.__human_time_limit is not None:
    #   human_seconds = self.__get_human_time(total_hands_played)
    #   human_time_progress = int(MathHelper.get_percentage(human_seconds, self.__human_time_limit))
    #   self.__results_progress = min(human_time_progress, 100)
    #   return

    # if self.__sim_time_limit is not None:
    #   sim_time_progress = int(time_elapsed_seconds / self.__sim_time_limit)
    #   self.__results_progress = min(sim_time_progress, 100)
    #   return

    # if self.__bankroll_goal != inf:
    #   bankroll_after_round = self.__game.get_ai_players()[0].get_bankroll()
    #   if bankroll_after_round <= self.__bankroll_fail:
    #     self.__results_progress = -100
    #     return
    #   else:
    #     winning_progress = int(((bankroll_after_round / self.__bankroll_goal) * 200) - 100)
    #     winning_progress = max(-100, min(100, winning_progress))
    #     self.__results_progress = winning_progress
    #     return

    # self.__results_progress = 0
    # return
    if self.__start_time is None:
      raise RuntimeError("start_time is None.")

    previous_progress = self.__results_progress

    sim_time_percentage_done = 0
    if self.__sim_time_limit:
      sim_time_percentage_done = MathHelper.get_percentage(time_elapsed_seconds, self.__sim_time_limit)
      if sim_time_percentage_done > 100:
        sim_time_percentage_done = 100

    human_time_percentage_done = 0
    if self.__human_time_limit:
      human_time = self.__get_human_time(total_hands_played)
      human_time_percentage_done = MathHelper.get_percentage(human_time, self.__human_time_limit)
      if human_time_percentage_done > 100:
        human_time_percentage_done = 100

    bankroll_fail_progress = 0
    bankroll_success_progress = 0
    if self.__bankroll_goal != inf:
      bankroll_after_round = self.__game.get_ai_players()[0].get_bankroll()
      bankroll_fail_progress = MathHelper.get_percentage(self.__bankroll_fail, bankroll_after_round)
      bankroll_fail_progress = max(0, bankroll_fail_progress)
      bankroll_success_progress = MathHelper.get_percentage(bankroll_after_round, self.__bankroll_goal)
      bankroll_success_progress = max(0, bankroll_success_progress)

    highest_progress = max(
      sim_time_percentage_done,
      human_time_percentage_done,
      bankroll_fail_progress,
      bankroll_success_progress,
      previous_progress
    )
    highest_progress = min(highest_progress, 100)
    self.__results_progress = int(highest_progress)
    return
