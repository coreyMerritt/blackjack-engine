import asyncio
from cmath import inf
from copy import deepcopy
import time
from typing import List
from entities.Game import Game
from entities.Hand import Hand
from models.core.HumanTime import HumanTime
from models.core.SimulationBounds import SimulationBounds
from models.core.results.SimulationMultiResultsFormatted import SimulationMultiResultsFormatted
from models.core.results.SimulationSingleResultsFormatted import SimulationSingleResultsFormatted
from models.core.results.SimulationMultiResults import SimulationMultiResults
from models.core.results.SimulationSingleResults import SimulationSingleResults
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult
from services.BlackjackLogger import BlackjackLogger


class SimulationEngine():
  __bankroll_goal: int
  __human_time_limit: int
  __sim_time_limit: int
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __single_results_progress: int
  __multi_results_progress: int
  __multi_start_time: float | None
  __game: Game
  __game_starting_point: Game
  __single_results: SimulationSingleResults
  __multi_results: SimulationMultiResults

  def __init__(self, game: Game, bounds: SimulationBounds, human_time: HumanTime):
    if bounds.bankroll_goal is None:
      self.__bankroll_goal = inf
    else:
      self.__bankroll_goal = bounds.bankroll_goal
    self.__human_time_limit = bounds.human_time_limit
    self.__sim_time_limit = bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__single_results_progress = 0
    self.__multi_results_progress = 0
    self.__multi_start_time = None
    self.__game = game
    self.__game_starting_point = deepcopy(game)
    self.__single_results = None
    self.__multi_results = None

  async def run(self, called_from_multi=False) -> None:
    if not called_from_multi:
      self.__full_reset()

    start_time = time.time()
    (starting_bankroll, highest_bankroll, lowest_bankroll) = (self.__game.get_ai_players()[0].get_bankroll(),) * 3
    counts = {"total": 0, "won": 0, "lost": 0, "drawn": 0, "blackjack": 0}
    profit_from_true = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    someone_has_bankroll = self.__game.someone_has_bankroll()
    bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()

    while(someone_has_bankroll and bankroll_is_below_goal):
      ai_player = self.__game.get_ai_players()[0]
      true_count = ai_player.calculate_true_count(self.__game.get_dealer().get_decks_remaining())
      self.__game.continue_until_state(GameState.CLEANUP)

      bankroll = self.__game.get_ai_players()[0].get_bankroll()
      if highest_bankroll < bankroll:
        highest_bankroll = bankroll
      if lowest_bankroll > bankroll:
        lowest_bankroll = bankroll

      for hand in ai_player.get_hands():
        self.__update_profits(hand, true_count, profit_from_true, counts)

      self.__game.finish_round()
      await self.__occasionally_yield_event_loop_control(counts["total"])
      self.__update_single_results_progress(counts["total"], time.time() - start_time)
      if self.__single_results_progress == 100 or self.__single_results_progress == -100:
        break

      someone_has_bankroll = self.__game.someone_has_bankroll()
      bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()

    simulation_time = round(time.time() - start_time, 2)
    percentages = {"won": 0.0, "lost": 0.0, "drawn": 0.0}
    percentages["won"] = (counts["won"] / counts["total"]) * 100
    percentages["lost"] = (counts["lost"] / counts["total"]) * 100
    percentages["drawn"] = (counts["drawn"] / counts["total"]) * 100
    ending_bankroll = round(self.__game.get_ai_players()[0].get_bankroll(), 0)
    total_profit = round(ending_bankroll - starting_bankroll, 2)
    for i in range(7):
      profit_from_true[i] = round(profit_from_true[i], 2)
    profit_per_hand = round(total_profit / counts["total"], 2)
    profit_per_hour = round(profit_per_hand * self.__hands_per_hour, 2)
    human_time = self.__get_human_time(counts["total"])
    self.__single_results = {
      "hands": {
        "counts": counts,
        "percentages": percentages
      },
      "bankroll": {
        "starting": starting_bankroll,
        "ending": ending_bankroll,
        "total_profit": total_profit,
        "profit_from_true": profit_from_true,
        "profit_per_hand": profit_per_hand,
        "profit_per_hour": profit_per_hour,
        "peak": highest_bankroll
      },
      "time": {
        "human_time": human_time,
        "simulation_time": simulation_time
      }
    }

  async def multi_run(self, runs: int) -> None:
    self.__full_reset()
    results = []
    sims_run = 0
    sims_won = 0
    sims_lost = 0
    sims_unfinished = 0
    self.__multi_start_time = time.time()
    for _ in range(0, runs):
      self.__reset_game()
      await self.run(True)
      results.append(self.get_single_results())
      ending_bankroll = self.__game.get_ai_players()[0].get_bankroll()
      sims_run += 1
      if ending_bankroll >= self.__bankroll_goal:
        sims_won += 1
      elif ending_bankroll <= 0:
        sims_lost += 1
      else:
        sims_unfinished += 1
      self.__multi_results_progress = int((sims_run / runs) * 100)

      if self.__sim_time_limit:
        if time.time() - self.__multi_start_time > self.__sim_time_limit:
          self.__multi_results_progress = 100
          break

      if self.__human_time_limit:
        total_hands_played = 0
        for result in results:
          total_hands_played += result["total_hands_played"]
        human_time = self.__get_human_time(total_hands_played)
        if human_time > self.__human_time_limit:
          self.__multi_results_progress = 100
          break

    end_time = time.time()
    success_rate = (sims_won / sims_run) * 100
    risk_of_ruin = (sims_lost / sims_run) * 100
    time_taken = end_time - self.__multi_start_time
    sim_results = {
      "sims_run": sims_run,
      "sims_won": sims_won,
      "sims_lost": sims_lost,
      "sims_unfinished": sims_unfinished,
      "success_rate": success_rate,
      "risk_of_ruin": risk_of_ruin,
      "time_taken": time_taken
    }
    self.__set_multi_results(results, sim_results)

  def get_single_results_progress(self) -> int:
    return self.__single_results_progress

  def get_multi_results_progress(self) -> int:
    return self.__multi_results_progress

  def get_single_results(self) -> SimulationSingleResults | None:
    if self.__single_results is None:
      return None
    return self.__single_results

  def get_multi_results(self) -> SimulationMultiResults | None:
    if self.__single_results is None:
      return None
    return self.__multi_results

  def get_single_results_formatted(self) -> SimulationSingleResultsFormatted:
    if not self.__single_results:
      return None

    counts = {"total": 0, "won": 0, "lost": 0, "drawn": 0}
    percentages = {"won": 0.0, "lost": 0.0, "drawn": 0.0}
    profit_from_true = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    total_hands_played = int(self.__single_results["hands"]["counts"]["total"])
    counts["won"] = int(self.__single_results["hands"]["counts"]["won"])
    counts["lost"] = int(self.__single_results["hands"]["counts"]["lost"])
    counts["drawn"] = int(self.__single_results["hands"]["counts"]["drawn"])
    percentages["won"] = float(self.__single_results["hands"]["percentages"]["won"])
    percentages["lost"] = float(self.__single_results["hands"]["percentages"]["lost"])
    percentages["drawn"] = float(self.__single_results["hands"]["percentages"]["drawn"])
    starting_bankroll = float(self.__single_results["bankroll"]["starting"])
    ending_bankroll = float(self.__single_results["bankroll"]["ending"])
    total_profit = float(self.__single_results["bankroll"]["total_profit"])
    for i in range(7):
      profit_from_true[i] = float(self.__single_results["bankroll"]["profit_from_true"][i])
    profit_per_hand = float(self.__single_results["bankroll"]["profit_per_hand"])
    profit_per_hour = float(self.__single_results["bankroll"]["profit_per_hour"])
    peak = float(self.__single_results["bankroll"]["peak"])
    human_time = float(self.__single_results["time"]["human_time"])
    simulation_time = float(self.__single_results["time"]["simulation_time"])
    return {
      "hands": {
        "counts": {
          "total": f"{total_hands_played:,}",
          "won": f"{counts["won"]:,}",
          "lost": f"{counts["lost"]:,}",
          "drawn": f"{counts["drawn"]:,}"
        },
        "percentages": {
          "won": f"{round(percentages["won"], 2):.2f}%",
          "lost": f"{round(percentages["lost"], 2):.2f}%",
          "drawn": f"{round(percentages["drawn"], 2):.2f}%"
        }
      },
      "bankroll": {
        "starting": self.__get_formatted_bankroll(starting_bankroll),
        "ending": self.__get_formatted_bankroll(ending_bankroll),
        "total_profit": self.__get_formatted_bankroll(total_profit),
        "profit_from_true": {
          0: self.__get_formatted_bankroll(profit_from_true[0]),
          1: self.__get_formatted_bankroll(profit_from_true[1]),
          2: self.__get_formatted_bankroll(profit_from_true[2]),
          3: self.__get_formatted_bankroll(profit_from_true[3]),
          4: self.__get_formatted_bankroll(profit_from_true[4]),
          5: self.__get_formatted_bankroll(profit_from_true[5]),
          6: self.__get_formatted_bankroll(profit_from_true[6])
        },
        "profit_per_hand": self.__get_formatted_bankroll(profit_per_hand),
        "profit_per_hour": self.__get_formatted_bankroll(profit_per_hour),
        "peak": self.__get_formatted_bankroll(peak)
      },
      "time": {
        "human_time": self.__get_time_formatted(human_time),
        "simulation_time": self.__get_time_formatted(simulation_time)
      }
    }

  def get_multi_results_formatted(self) -> SimulationMultiResultsFormatted | None:
    if not self.__multi_results:
      return None
    sims_run = int(self.__multi_results["sims_run"])
    sims_won = int(self.__multi_results["sims_won"])
    sims_lost = int(self.__multi_results["sims_lost"])
    sims_unfinished = int(self.__multi_results["sims_unfinished"])
    success_rate = float(self.__multi_results["success_rate"])
    risk_of_ruin = float(self.__multi_results["risk_of_ruin"])
    time_taken = self.__get_time_formatted(float(self.__multi_results["time_taken"]))
    average = self.__multi_results["average"]
    self.__set_single_results(average)
    formatted_average = self.get_single_results_formatted()
    return {
      "sims_run": f"{sims_run:,}",
      "sims_won": f"{sims_won:,}",
      "sims_lost": f"{sims_lost:,}",
      "sims_unfinished": f"{sims_unfinished:,}",
      "success_rate": f"{round(success_rate, 2):.2f}%",
      "risk_of_ruin": f"{round(risk_of_ruin, 2):.2f}%",
      "time_taken": time_taken,
      "average": formatted_average
    }

  def __calculate_if_bankroll_is_below_goal(self) -> bool:
    if self.__bankroll_goal:
      return self.__game.get_ai_players()[0].get_bankroll() < self.__bankroll_goal
    else:
      return True

  def __get_human_time(self, total_hands_played: int) -> float:
    hours = total_hands_played / self.__hands_per_hour
    minutes = hours * 60
    seconds = minutes * 60
    human_time = round(seconds, 2)
    return human_time

  def __get_formatted_bankroll(self, value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"

  def __get_time_formatted(self, seconds: float) -> str:
    if seconds > 60:
      minutes = seconds / 60
      if minutes > 60:
        hours = minutes / 60
        if hours > self.__hours_per_day:
          days = hours / self.__hours_per_day
          if days > self.__days_per_week:
            weeks = days / self.__days_per_week
            if weeks > 4.345:
              months = weeks / 4.345
              if months > 12:
                years = months / 12
                return f"{years:,.2f} years"
              else:
                return f"{months:,.2f} months"
            else:
              return f"{weeks:,.2f} weeks"
          else:
            return f"{days:,.2f} days"
        else:
          return f"{hours:,.2f} hrs"
      else:
        return f"{minutes:,.2f} mins"
    else:
      return f"{seconds:,.2f} secs"

  def __set_multi_results(self, results_list, sim_results) -> dict:
    total_runs = len(results_list)
    if total_runs == 0:
      return {}

    summed = SimulationSingleResults().model_dump(by_alias=True)
    for r in results_list:
      summed["hands"]["counts"]["total"] += int(r["hands"]["counts"]["total"])
      summed["hands"]["counts"]["won"] += int(r["hands"]["counts"]["won"])
      summed["hands"]["counts"]["lost"] += int(r["hands"]["counts"]["lost"])
      summed["hands"]["counts"]["drawn"] += int(r["hands"]["counts"]["drawn"])
      summed["bankroll"]["starting"] += float(r["bankroll"]["starting"])
      summed["bankroll"]["ending"] += float(r["bankroll"]["ending"])
      summed["bankroll"]["total_profit"] += float(r["bankroll"]["total_profit"])
      for i in range(7):
        summed["bankroll"]["profit_from_true"][i] += float(r["bankroll"]["profit_from_true"][i])
      summed["bankroll"]["profit_per_hand"] += float(r["bankroll"]["profit_per_hand"])
      summed["bankroll"]["profit_per_hour"] += float(r["bankroll"]["profit_per_hour"])
      summed["bankroll"]["peak"] += float(r["bankroll"]["peak"])
      summed["time"]["human_time"] += float(r["time"]["human_time"])
      summed["time"]["simulation_time"] += float(r["time"]["simulation_time"])

    percentages = {"won": 0.0, "lost": 0.0, "drawn": 0.0}
    percentages["won"] = (summed["hands"]["counts"]["won"] / summed["hands"]["counts"]["total"]) * 100
    percentages["lost"] = (summed["hands"]["counts"]["lost"] / summed["hands"]["counts"]["total"]) * 100
    percentages["drawn"] = (summed["hands"]["counts"]["drawn"] / summed["hands"]["counts"]["total"]) * 100
    averaged = SimulationSingleResults().model_dump(by_alias=True)
    averaged["hands"]["counts"]["total"] = summed["hands"]["counts"]["total"] // total_runs
    averaged["hands"]["counts"]["won"] = summed["hands"]["counts"]["won"] // total_runs
    averaged["hands"]["counts"]["lost"] = summed["hands"]["counts"]["lost"] // total_runs
    averaged["hands"]["counts"]["drawn"] = summed["hands"]["counts"]["drawn"] // total_runs
    averaged["hands"]["percentages"]["won"] = percentages["won"] / total_runs
    averaged["hands"]["percentages"]["lost"] = percentages["lost"] / total_runs
    averaged["hands"]["percentages"]["drawn"] = percentages["drawn"] / total_runs
    averaged["bankroll"]["starting"] = summed["bankroll"]["starting"] / total_runs
    averaged["bankroll"]["ending"] = summed["bankroll"]["ending"] / total_runs
    averaged["bankroll"]["total_profit"] = summed["bankroll"]["total_profit"] / total_runs
    for i in range(7):
      averaged["bankroll"]["profit_from_true"][i] = summed["bankroll"]["profit_from_true"][i] / total_runs
    averaged["bankroll"]["profit_per_hand"] = summed["bankroll"]["profit_per_hand"] / total_runs
    averaged["bankroll"]["profit_per_hour"] = summed["bankroll"]["profit_per_hour"] / total_runs
    averaged["bankroll"]["peak"] = summed["bankroll"]["peak"] / total_runs
    averaged["time"]["human_time"] = summed["time"]["human_time"] / total_runs
    averaged["time"]["simulation_time"] = summed["time"]["simulation_time"] / total_runs

    multi_sim = SimulationMultiResults().model_dump(by_alias=True)
    multi_sim["sims_run"] = sim_results["sims_run"]
    multi_sim["sims_won"] = sim_results["sims_won"]
    multi_sim["sims_lost"] = sim_results["sims_lost"]
    multi_sim["sims_unfinished"] = sim_results["sims_unfinished"]
    multi_sim["success_rate"] = sim_results["success_rate"]
    multi_sim["risk_of_ruin"] = sim_results["risk_of_ruin"]
    multi_sim["time_taken"] = sim_results["time_taken"]
    multi_sim["average"] = averaged
    self.__multi_results = multi_sim

  def __full_reset(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)
    self.__single_results_progress = 0
    self.__multi_results_progress = 0
    self.__single_results = None
    self.__multi_results = None

  async def __occasionally_yield_event_loop_control(self, total_hands_played) -> None:
    if total_hands_played % 100 == 0:
      await asyncio.sleep(0)

  def __reset_game(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)

  def __set_single_results(self, results: SimulationSingleResults) -> None:
    self.__single_results = results

  def __update_profits(self, hand: Hand, true_count: int, profit_from_true: List[float], counts: dict) -> None:
    hand_result = hand.get_result()
    bet = hand.get_bet()
    initial_bet = hand.get_initial_bet()
    BlackjackLogger.debug(f"\t\tBet history: {initial_bet}")
    payout = hand.get_payout()
    if true_count > 6:
      adjusted_true_count = 6
    elif true_count < 0:
      adjusted_true_count = 0
    else:
      adjusted_true_count = true_count
    if hand_result == HandResult.LOSS:
      profit_from_true[adjusted_true_count] -= bet
    profit_from_true[adjusted_true_count] += payout
    if hand_result == HandResult.BLACKJACK:
      counts["blackjack"] += 1
      counts["won"] += 1
    elif hand_result == HandResult.WIN:
      counts["won"] += 1
    elif hand_result == HandResult.LOSS:
      counts["lost"] += 1
    elif hand_result == HandResult.DRAW:
      counts["drawn"] += 1
    counts["total"] += 1
    BlackjackLogger.debug(f"\t\tHand result: {hand_result}")
    BlackjackLogger.debug(f"\t\tPayout: {payout}")

  def __update_single_results_progress(self, total_hands_played: int, time_elapsed_seconds: float) -> None:
    if self.__bankroll_goal != inf:
      bankroll_after_round = self.__game.get_ai_players()[0].get_bankroll()
      if bankroll_after_round == 0:
        self.__single_results_progress = -100
        return
      else:
        winning_progress = int(((bankroll_after_round / self.__bankroll_goal) * 200) - 100)
        winning_progress = max(-100, min(100, winning_progress))
        self.__single_results_progress = winning_progress
        return

    if self.__human_time_limit is not None:
      human_seconds = self.__get_human_time(total_hands_played)
      human_time_progress = int(human_seconds / self.__human_time_limit) * 100
      self.__single_results_progress = min(human_time_progress, 100)
      return

    if self.__sim_time_limit is not None:
      sim_time_progress = int(time_elapsed_seconds / self.__sim_time_limit)
      self.__single_results_progress = min(sim_time_progress, 100)
      return

    self.__single_results_progress = 0
    return
