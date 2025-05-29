import asyncio
from copy import deepcopy
import time
from entities.Game import Game
from models.core.results.SimulationMultiResultsFormatted import SimulationMultiResultsFormatted
from models.core.results.SimulationSingleResultsFormatted import SimulationSingleResultsFormatted
from models.core.results.SimulationMultiResults import SimulationMultiResults
from models.core.results.SimulationSingleResults import SimulationSingleResults
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult


class SimulationEngine():
  __money_goal: int
  __game: Game
  __game_starting_point: Game
  __single_results: SimulationSingleResults
  __single_results_status: int
  __multi_results: SimulationMultiResults
  __multi_results_status: int

  def __init__(self, game: Game, money_goal: int):
    self.__money_goal = money_goal
    self.__game = game
    self.__game_starting_point = deepcopy(game)
    self.__single_results = None
    self.__single_results_status = 0
    self.__multi_results = None
    self.__multi_results_status = 0

  def reset_game(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)

  def full_reset(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)
    self.__single_results = None
    self.__single_results_status = 0
    self.__multi_results = None
    self.__multi_results_status = 0

  async def multi_run(self, runs: int) -> None:
    self.full_reset()
    results = []
    sims_run = 0
    sims_won = 0
    sims_lost = 0
    start_time = time.time()
    for _ in range(0, runs):
      self.reset_game()
      await self.run(True)
      results.append(self.get_single_results())
      sims_run += 1
      if self.__game.get_ai_players()[0].get_money() >= self.__money_goal:
        sims_won += 1
      else:
        sims_lost += 1
      self.__multi_results_status = int((sims_run / runs) * 100)
    end_time = time.time()
    success_rate = (sims_won / sims_run) * 100
    risk_of_ruin = (sims_lost / sims_run) * 100
    time_taken = end_time - start_time
    sim_results = {
      "sims_run": sims_run,
      "sims_won": sims_won,
      "sims_lost": sims_lost,
      "success_rate": success_rate,
      "risk_of_ruin": risk_of_ruin,
      "time_taken": time_taken
    }
    self.__set_multi_results(results, sim_results)

  async def run(self, called_from_multi=False) -> None:
    if not called_from_multi:
      self.full_reset()
    start_time = time.time()
    starting_money = self.__game.get_ai_players()[0].get_money()
    highest_money = self.__game.get_ai_players()[0].get_money()
    hands_won_count = 0
    hands_lost_count = 0
    hands_drawn_count = 0

    while(self.__game.someone_has_money() and self.__game.get_ai_players()[0].get_money() < self.__money_goal):
      self.__game.continue_until_state(GameState.CLEANUP)
      money = self.__game.get_ai_players()[0].get_money()

      if highest_money < money:
        highest_money = money

      for player in self.__game.get_all_players_except_dealer():
        for hand in player.get_hands():
          hand_result = hand.get_result()
          if hand_result == HandResult.WON:
            hands_won_count += 1
          elif hand_result == HandResult.LOST:
            hands_lost_count += 1
          elif hand_result == HandResult.DREW:
            hands_drawn_count += 1
      self.__game.finish_round()
      total_hands_played = hands_won_count + hands_lost_count + hands_drawn_count
      if total_hands_played % 100 == 0:
        await asyncio.sleep(0)

    simulation_time = round(time.time() - start_time, 2)
    total_hands_played = hands_won_count + hands_lost_count + hands_drawn_count
    hands_won_percent = (hands_won_count / total_hands_played) * 100
    hands_lost_percent = (hands_lost_count / total_hands_played) * 100
    hands_drawn_percent = (hands_drawn_count / total_hands_played) * 100
    ending_money = round(self.__game.get_ai_players()[0].get_money(), 0)
    total_profit = round(ending_money - starting_money, 2)
    profit_per_hand = round(total_profit / total_hands_played, 2)
    profit_per_hour = round(profit_per_hand * 60, 2)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    hands_per_hour = 60
    hours = total_hands_played / hands_per_hour
    minutes = hours * 60
    seconds = minutes * 60
    human_time = round(seconds, 2)
    self.__single_results = {
      "total_hands_played": total_hands_played,
      "hands_won": {
        "count": hands_won_count,
        "percent": hands_won_percent
      },
      "hands_lost": {
        "count": hands_lost_count,
        "percent": hands_lost_percent
      },
      "hands_drawn": {
        "count": hands_drawn_count,
        "percent": hands_drawn_percent
      },
      "money": {
        "starting": starting_money,
        "ending": ending_money,
        "total_profit": total_profit,
        "profit_per_hand": profit_per_hand,
        "profit_per_hour": profit_per_hour,
        "peak": highest_money
      },
      "time": {
        "human_time": human_time,
        "simulation_time": simulation_time
      }
    }

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
    total_hands_played = int(self.__single_results["total_hands_played"])
    hands_won_count = int(self.__single_results["hands_won"]["count"])
    hands_won_percent = float(self.__single_results["hands_won"]["percent"])
    hands_lost_count = int(self.__single_results["hands_lost"]["count"])
    hands_lost_percent = float(self.__single_results["hands_lost"]["percent"])
    hands_drawn_count = int(self.__single_results["hands_drawn"]["count"])
    hands_drawn_percent = float(self.__single_results["hands_drawn"]["percent"])
    starting_money = float(self.__single_results["money"]["starting"])
    ending_money = float(self.__single_results["money"]["ending"])
    total_profit = float(self.__single_results["money"]["total_profit"])
    profit_per_hand = float(self.__single_results["money"]["profit_per_hand"])
    profit_per_hour = float(self.__single_results["money"]["profit_per_hour"])
    peak = float(self.__single_results["money"]["peak"])
    human_time = float(self.__single_results["time"]["human_time"])
    simulation_time = float(self.__single_results["time"]["simulation_time"])
    return {
      "total_hands_played": f"{total_hands_played:,}",
      "hands_won": {
        "count": f"{hands_won_count:,}",
        "percent": f"{round(hands_won_percent, 2):.2f}%"
      },
      "hands_lost": {
        "count": f"{hands_lost_count:,}",
        "percent": f"{round(hands_lost_percent, 2):.2f}%"
      },
      "hands_drawn": {
        "count": f"{hands_drawn_count:,}",
        "percent": f"{round(hands_drawn_percent, 2):.2f}%"
      },
      "money": {
        "starting": self.__format_money(starting_money),
        "ending": self.__format_money(ending_money),
        "total_profit": self.__format_money(total_profit),
        "profit_per_hand": self.__format_money(profit_per_hand),
        "profit_per_hour": self.__format_money(profit_per_hour),
        "peak": self.__format_money(peak)
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
      "success_rate": f"{round(success_rate, 2):.2f}%",
      "risk_of_ruin": f"{round(risk_of_ruin, 2):.2f}%",
      "time_taken": time_taken,
      "average": formatted_average
    }

  def get_single_results_status(self) -> int:
    return self.__single_results_status

  def get_multi_results_status(self) -> int:
    return self.__multi_results_status

  def __get_time_formatted(self, seconds: float) -> str:
    if seconds > 60:
      minutes = seconds / 60
      if minutes > 60:
        hours = minutes / 60
        if hours > 24:
          days = hours / 24
          if days > 7:
            weeks = days / 7
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

  def __set_single_results(self, results: SimulationSingleResults) -> None:
    self.__single_results = results

  def __set_multi_results(self, results_list, sim_results) -> dict:
    total_runs = len(results_list)
    if total_runs == 0:
      return {}

    summed = SimulationSingleResults().model_dump()
    for r in results_list:
      summed["total_hands_played"] += int(r["total_hands_played"])
      summed["hands_won"]["count"] += int(r["hands_won"]["count"])
      summed["hands_won"]["percent"] += int(r["hands_won"]["percent"])
      summed["hands_lost"]["count"] += int(r["hands_lost"]["count"])
      summed["hands_lost"]["percent"] += int(r["hands_lost"]["percent"])
      summed["hands_drawn"]["count"] += int(r["hands_drawn"]["count"])
      summed["hands_drawn"]["percent"] += int(r["hands_drawn"]["percent"])
      summed["money"]["starting"] += float(r["money"]["starting"])
      summed["money"]["ending"] += float(r["money"]["ending"])
      summed["money"]["total_profit"] += float(r["money"]["total_profit"])
      summed["money"]["profit_per_hand"] += float(r["money"]["profit_per_hand"])
      summed["money"]["profit_per_hour"] += float(r["money"]["profit_per_hour"])
      summed["money"]["peak"] += float(r["money"]["peak"])
      summed["time"]["human_time"] += float(r["time"]["human_time"])
      summed["time"]["simulation_time"] += float(r["time"]["simulation_time"])

    averaged = SimulationSingleResults().model_dump()
    averaged["total_hands_played"] = summed["total_hands_played"] // total_runs
    averaged["hands_won"]["count"] = summed["hands_won"]["count"] // total_runs
    averaged["hands_won"]["percent"] = summed["hands_won"]["percent"] / total_runs
    averaged["hands_lost"]["count"] = summed["hands_lost"]["count"] // total_runs
    averaged["hands_lost"]["percent"] = summed["hands_lost"]["percent"] / total_runs
    averaged["hands_drawn"]["count"] = summed["hands_drawn"]["count"] // total_runs
    averaged["hands_drawn"]["percent"] = summed["hands_drawn"]["percent"] / total_runs
    averaged["money"]["starting"] = summed["money"]["starting"] / total_runs
    averaged["money"]["ending"] = summed["money"]["ending"] / total_runs
    averaged["money"]["total_profit"] = summed["money"]["total_profit"] / total_runs
    averaged["money"]["profit_per_hand"] = summed["money"]["profit_per_hand"] / total_runs
    averaged["money"]["profit_per_hour"] = summed["money"]["profit_per_hour"] / total_runs
    averaged["money"]["peak"] = summed["money"]["peak"] / total_runs
    averaged["time"]["human_time"] = summed["time"]["human_time"] / total_runs
    averaged["time"]["simulation_time"] = summed["time"]["simulation_time"] / total_runs

    multi_sim = SimulationMultiResults().model_dump()
    multi_sim["sims_run"] = sim_results["sims_run"]
    multi_sim["sims_won"] = sim_results["sims_won"]
    multi_sim["sims_lost"] = sim_results["sims_lost"]
    multi_sim["success_rate"] = sim_results["success_rate"]
    multi_sim["risk_of_ruin"] = sim_results["risk_of_ruin"]
    multi_sim["time_taken"] = sim_results["time_taken"]
    multi_sim["average"] = averaged
    self.__multi_results = multi_sim

  def __format_money(self, value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"
