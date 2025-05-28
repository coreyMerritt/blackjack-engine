import time
from entities.Game import Game
from models.api.SimulationResultsRes import SimulationResults


class SimulationEngine():
  __money_goal: int
  __game: Game
  __results: SimulationResults


  def __init__(self, game: Game, money_goal: int) -> None:
    self.__money_goal = money_goal
    self.__game = game

  def run(self) -> None:
    start_time = time.time()
    hand_count = 0
    starting_money = self.__game.get_ai_players()[0].get_money()
    previous_money = self.__game.get_ai_players()[0].get_money()
    highest_money = self.__game.get_ai_players()[0].get_money()
    hands_won = 0
    hands_lost = 0
    hands_drawn = 0

    while(self.__game.someone_has_money() and self.__game.get_ai_players()[0].get_money() < self.__money_goal):
      previous_money = self.__game.get_ai_players()[0].get_money()
      self.__game.finish_round()
      hand_count += 1
      money = self.__game.get_ai_players()[0].get_money()

      if highest_money < money:
        highest_money = money

      if money > previous_money:
        hands_won += 1
      elif money < previous_money:
        hands_lost += 1
      else:
        hands_drawn += 1

      runtime = time.time() - start_time
      if runtime > 60:
        break

    simulation_time = round(time.time() - start_time, 2)
    ending_money = round(self.__game.get_ai_players()[0].get_money(), 0)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    hands_per_hour = 60
    human_time = f"{round(hand_count / hands_per_hour, 2)} hrs"   # Currently assumes 60 hands/hrs
    total_hands_played = hands_won + hands_lost + hands_drawn
    money_diff = round(ending_money - starting_money, 2)
    money_made_per_hand = round(money_diff / total_hands_played, 2)
    money_made_per_hour = round(money_made_per_hand * 60, 2)
    self.__results = {
      "total_hands_played": f"{total_hands_played:,}",
      "hands_won": {
        "count": f"{hands_won:,}",
        "percent": f"{round((hands_won / total_hands_played) * 100, 2)}%"
      },
      "hands_lost": {
        "count": f"{hands_lost:,}",
        "percent": f"{round((hands_lost / total_hands_played) * 100, 2)}%"
      },
      "hands_drawn": {
        "count": f"{hands_drawn:,}",
        "percent": f"{round((hands_drawn / total_hands_played) * 100, 2)}%"
      },
      "money": {
        "total profit": self._format_money(money_diff),
        "profit_per_hand": self._format_money(money_made_per_hand),
        "profit_per_hour": self._format_money(money_made_per_hour),
        "peak": self._format_money(highest_money)
      },
      "time": {
        "human_time_taken": human_time,
        "simulation_time": simulation_time
      }
    }

  def get_results(self) -> SimulationResults:
    return self.__results

  def _format_money(self, value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"
