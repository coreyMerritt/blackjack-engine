from copy import deepcopy
import time
from entities.Game import Game
from models.api.SimulationResultsFormattedRes import SimulationResultsFormattedRes
from models.api.SimulationResultsRes import SimulationResultsRes
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult


class SimulationEngine():
  __money_goal: int
  __game: Game
  __game_starting_point: Game
  __results: SimulationResultsRes


  def __init__(self, game: Game, money_goal: int):
    self.__money_goal = money_goal
    self.__game = game
    self.__game_starting_point = deepcopy(game)
    self.__results = None

  def reset(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)

  async def multi_run(self, runs: int) -> None:
    results = []
    for _ in range(runs):
      self.reset()
      await self.run()
      results.append(self.get_results())
    average_results = self.__get_average_results(results)
    self.__results = average_results

  async def run(self) -> None:
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
    human_time = round(total_hands_played / hands_per_hour, 2)
    self.__results = {
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

  def get_results(self) -> SimulationResultsRes:
    if self.__results is None:
      return None
    return self.__results

  def get_results_formatted(self) -> SimulationResultsFormattedRes:
    total_hands_played = self.__results["total_hands_played"]
    hands_won_count = self.__results["hands_won"]["count"]
    hands_won_percent = self.__results["hands_won"]["percent"]
    hands_lost_count = self.__results["hands_lost"]["count"]
    hands_lost_percent = self.__results["hands_lost"]["percent"]
    hands_drawn_count = self.__results["hands_drawn"]["count"]
    hands_drawn_percent = self.__results["hands_drawn"]["percent"]
    starting_money = self.__results["money"]["starting"]
    ending_money = self.__results["money"]["ending"]
    total_profit = self.__results["money"]["total_profit"]
    profit_per_hand = self.__results["money"]["profit_per_hand"]
    profit_per_hour = self.__results["money"]["profit_per_hour"]
    peak = self.__results["money"]["peak"]
    human_time = self.__results["time"]["human_time"]
    simulation_time = self.__results["time"]["simulation_time"]

    return {
      "total_hands_played": f"{total_hands_played:,}",
      "hands_won": {
        "count": f"{hands_won_count:,}",
        "percent": f"{round(hands_won_percent, 2)}%"
      },
      "hands_lost": {
        "count": f"{hands_lost_count:,}",
        "percent": f"{round(hands_lost_percent, 2)}%"
      },
      "hands_drawn": {
        "count": f"{hands_drawn_count:,}",
        "percent": f"{round(hands_drawn_percent, 2)}%"
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
        "human_time": f"{human_time}hrs",
        "simulation_time": f"{simulation_time}s"
      }
    }

  def __get_average_results(self, results_list) -> dict:

    total_runs = len(results_list)
    if total_runs == 0:
      return {}

    summed = {
      "total_hands_played": 0,
      "hands_won": {
        "count": 0,
        "percent": 0
      },
      "hands_lost": {
        "count": 0,
        "percent": 0
      },
      "hands_drawn": {
        "count": 0,
        "percent": 0
      },
      "money": {
        "starting": 0.0,
        "ending": 0.0,
        "total_profit": 0.0,
        "profit_per_hand": 0.0,
        "profit_per_hour": 0.0,
        "peak": 0.0
      },
      "time": {
        "human_time": 0.0,
        "simulation_time": 0.0
      }
    }

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

    self.__results = summed
    return self.get_results_formatted()

  def __format_money(self, value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"
