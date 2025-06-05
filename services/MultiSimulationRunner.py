import json
import time
from typing import List
from entities.Game import Game
from models.core.HumanTime import HumanTime
from models.core.SimulationBounds import SimulationBounds
from models.core.results.SimulationMultiResultsFormatted import SimulationMultiResultsFormatted
from models.core.results.SimulationMultiResults import SimulationMultiResults
from models.core.results.SimulationSingleResults import SimulationSingleResults
from services.BlackjackLogger import BlackjackLogger
from services.SingleSimulationRunner import SingleSimulationRunner


class MultiSimulationRunner():
  __human_time_limit: int
  __sim_time_limit: int
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __results_progress: int
  __start_time: float | None
  __results: SimulationMultiResults

  def __init__(self, game: Game, bounds: SimulationBounds, human_time: HumanTime):
    self.__single_sim_runner = SingleSimulationRunner(game, bounds, human_time)
    self.__human_time_limit = bounds.human_time_limit
    self.__sim_time_limit = bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__results_progress = 0
    self.__start_time = None
    self.__results = None

  async def run(self, runs: int) -> None:
    self.__full_reset()
    single_sim_results = []
    sims = { "run": 0, "won": 0, "lost": 0, "unfinished": 0 }
    self.__start_time = time.time()

    for _ in range(0, runs):
      self.__single_sim_runner.reset_game()
      await self.__single_sim_runner.run(True)
      single_sim_results.append(self.__single_sim_runner.get_results())
      self.__count_sim(sims)
      self.__update_results_progress(single_sim_results, sims, runs)
      if self.__results_progress == 100:
        break

    end_time = time.time()
    success_rate = (sims["won"] / sims["run"]) * 100
    risk_of_ruin = (sims["lost"] / sims["run"]) * 100
    time_taken = end_time - self.__start_time
    multi_sim_results = {
      "sims_run": sims["run"],
      "sims_won": sims["won"],
      "sims_lost": sims["lost"],
      "sims_unfinished": sims["unfinished"],
      "success_rate": success_rate,
      "risk_of_ruin": risk_of_ruin,
      "time_taken": time_taken
    }
    self.__set_results(single_sim_results, multi_sim_results)

  def get_results(self) -> SimulationMultiResults | None:
    if not self.__results:
      return None
    return self.__results

  def get_results_progress(self) -> int:
    return self.__results_progress

  def get_results_formatted(self) -> SimulationMultiResultsFormatted | None:
    if not self.__results:
      return None
    sims_run = int(self.__results["sims_run"])
    sims_won = int(self.__results["sims_won"])
    sims_lost = int(self.__results["sims_lost"])
    sims_unfinished = int(self.__results["sims_unfinished"])
    success_rate = float(self.__results["success_rate"])
    risk_of_ruin = float(self.__results["risk_of_ruin"])
    time_taken = self.__get_time_formatted(float(self.__results["time_taken"]))
    average = self.__results["single_sim_averages"]
    self.__single_sim_runner.set_results(average)
    formatted_single_sim_averages = self.__single_sim_runner.get_results_formatted()
    multi_sim_info_formatted = {
      "sims_run": f"{sims_run:,}",
      "sims_won": f"{sims_won:,}",
      "sims_lost": f"{sims_lost:,}",
      "sims_unfinished": f"{sims_unfinished:,}",
      "success_rate": f"{round(success_rate, 2):.2f}%",
      "risk_of_ruin": f"{round(risk_of_ruin, 2):.2f}%",
      "time_taken": time_taken,
    }

    return {
      "multi_sim_info": multi_sim_info_formatted,
      "single_sim_averages": formatted_single_sim_averages
    }

  def __get_human_time(self, total_hands_played: int) -> float:
    hours = total_hands_played / self.__hands_per_hour
    minutes = hours * 60
    seconds = minutes * 60
    return seconds

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

  def __get_single_sims_summed(self, single_sim_results: List[dict]) -> dict:
    single_sims_summed = SimulationSingleResults().model_dump(by_alias=True)
    for r in single_sim_results:
      single_sims_summed["hands"]["counts"]["total"] += int(r["hands"]["counts"]["total"])
      single_sims_summed["hands"]["counts"]["blackjack"] += int(r["hands"]["counts"]["blackjack"])
      single_sims_summed["hands"]["counts"]["won"] += int(r["hands"]["counts"]["won"])
      single_sims_summed["hands"]["counts"]["drawn"] += int(r["hands"]["counts"]["drawn"])
      single_sims_summed["hands"]["counts"]["lost"] += int(r["hands"]["counts"]["lost"])
      single_sims_summed["hands"]["counts"]["surrendered"] += int(r["hands"]["counts"]["surrendered"])
      single_sims_summed["bankroll"]["starting"] += float(r["bankroll"]["starting"])
      single_sims_summed["bankroll"]["ending"] += float(r["bankroll"]["ending"])
      single_sims_summed["bankroll"]["total_profit"] += float(r["bankroll"]["total_profit"])
      for i in range(7):
        single_sims_summed["bankroll"]["profit_from_true"][i] += float(r["bankroll"]["profit_from_true"][i])
      single_sims_summed["bankroll"]["profit_per_hand"] += float(r["bankroll"]["profit_per_hand"])
      single_sims_summed["bankroll"]["profit_per_hour"] += float(r["bankroll"]["profit_per_hour"])
      single_sims_summed["bankroll"]["peak"] += float(r["bankroll"]["peak"])
      single_sims_summed["time"]["human_time"] += float(r["time"]["human_time"])
      single_sims_summed["time"]["simulation_time"] += float(r["time"]["simulation_time"])
    return single_sims_summed

  def __get_percentages(self, single_sims_summed: dict) -> dict:
    s = single_sims_summed
    percentages = { "blackjack": 0.0, "won": 0.0, "lost": 0.0, "drawn": 0.0, "surrendered": 0.0 }
    percentages["blackjack"] = (s["hands"]["counts"]["blackjack"] / s["hands"]["counts"]["total"]) * 100
    percentages["won"] = (s["hands"]["counts"]["won"] / s["hands"]["counts"]["total"]) * 100
    percentages["drawn"] = (s["hands"]["counts"]["drawn"] / s["hands"]["counts"]["total"]) * 100
    percentages["lost"] = (s["hands"]["counts"]["lost"] / s["hands"]["counts"]["total"]) * 100
    percentages["surrendered"] = (s["hands"]["counts"]["surrendered"] / s["hands"]["counts"]["total"]) * 100
    return percentages

  def __get_single_sims_averaged(self, single_sims_summed: dict, total_runs: int, percentages: dict) -> dict:
    single_sims_averaged = SimulationSingleResults().model_dump(by_alias=True)
    s = single_sims_summed
    single_sims_averaged["hands"]["counts"]["total"] = s["hands"]["counts"]["total"] / total_runs
    single_sims_averaged["hands"]["counts"]["blackjack"] = s["hands"]["counts"]["blackjack"] / total_runs
    single_sims_averaged["hands"]["counts"]["won"] = s["hands"]["counts"]["won"] / total_runs
    single_sims_averaged["hands"]["counts"]["drawn"] = s["hands"]["counts"]["drawn"] / total_runs
    single_sims_averaged["hands"]["counts"]["lost"] = s["hands"]["counts"]["lost"] / total_runs
    single_sims_averaged["hands"]["counts"]["surrendered"] = s["hands"]["counts"]["surrendered"] / total_runs
    single_sims_averaged["hands"]["percentages"]["blackjack"] = percentages["blackjack"]
    single_sims_averaged["hands"]["percentages"]["won"] = percentages["won"]
    single_sims_averaged["hands"]["percentages"]["drawn"] = percentages["drawn"]
    single_sims_averaged["hands"]["percentages"]["lost"] = percentages["lost"]
    single_sims_averaged["hands"]["percentages"]["surrendered"] = percentages["surrendered"]
    single_sims_averaged["bankroll"]["starting"] = s["bankroll"]["starting"] / total_runs
    single_sims_averaged["bankroll"]["ending"] = s["bankroll"]["ending"] / total_runs
    single_sims_averaged["bankroll"]["total_profit"] = s["bankroll"]["total_profit"] / total_runs
    for i in range(7):
      single_sims_averaged["bankroll"]["profit_from_true"][i] = s["bankroll"]["profit_from_true"][i] / total_runs
    single_sims_averaged["bankroll"]["profit_per_hand"] = s["bankroll"]["profit_per_hand"] / total_runs
    single_sims_averaged["bankroll"]["profit_per_hour"] = s["bankroll"]["profit_per_hour"] / total_runs
    single_sims_averaged["bankroll"]["peak"] = s["bankroll"]["peak"] / total_runs
    single_sims_averaged["time"]["human_time"] = s["time"]["human_time"] / total_runs
    single_sims_averaged["time"]["simulation_time"] = s["time"]["simulation_time"] / total_runs
    return single_sims_averaged

  def __get_all_sims_results(self, single_sims_averaged: List[dict], multi_sim_results: dict) -> dict:
    all_sims_results = SimulationMultiResults().model_dump(by_alias=True)
    all_sims_results["sims_run"] = multi_sim_results["sims_run"]
    all_sims_results["sims_won"] = multi_sim_results["sims_won"]
    all_sims_results["sims_lost"] = multi_sim_results["sims_lost"]
    all_sims_results["sims_unfinished"] = multi_sim_results["sims_unfinished"]
    all_sims_results["success_rate"] = multi_sim_results["success_rate"]
    all_sims_results["risk_of_ruin"] = multi_sim_results["risk_of_ruin"]
    all_sims_results["time_taken"] = multi_sim_results["time_taken"]
    all_sims_results["single_sim_averages"] = single_sims_averaged
    return all_sims_results

  def __set_results(self, single_sim_results: List[dict], multi_sim_results: dict) -> dict:
    total_runs = len(single_sim_results)
    if total_runs == 0:
      return {}
    single_sims_summed = self.__get_single_sims_summed(single_sim_results)
    percentages = self.__get_percentages(single_sims_summed)
    single_sims_averaged = self.__get_single_sims_averaged(single_sims_summed, total_runs, percentages)
    assert sum(single_sims_averaged["bankroll"]["profit_from_true"]) == single_sims_averaged["bankroll"]["total_profit"]
    all_sims_results = self.__get_all_sims_results(single_sims_averaged, multi_sim_results)
    self.__results = all_sims_results

  def __count_sim(self, sims: dict) -> None:
    ending_bankroll = self.__single_sim_runner.get_bankroll()
    bankroll_goal = self.__single_sim_runner.get_bankroll_goal()
    sims["run"] += 1
    if ending_bankroll >= bankroll_goal:
      sims["won"] += 1
    elif ending_bankroll <= 0:
      sims["lost"] += 1
    else:
      sims["unfinished"] += 1

  def __full_reset(self) -> None:
    self.__results_progress = 0
    self.__results = None
    self.__start_time = None

  def __update_results_progress(self, single_sim_results: dict, sims: dict, runs: int) -> None:
    self.__results_progress = int((sims["run"] / runs) * 100)
    if self.__sim_time_limit:
      if time.time() - self.__start_time > self.__sim_time_limit:
        self.__results_progress = 100

    if self.__human_time_limit:
      total_hands_played = 0
      for result in single_sim_results:
        total_hands_played += result["total_hands_played"]
      human_time = self.__get_human_time(total_hands_played)
      if human_time > self.__human_time_limit:
        self.__results_progress = 100
