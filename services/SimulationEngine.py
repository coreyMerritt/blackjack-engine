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
    highest_money = self.__game.get_ai_players()[0].get_money()

    while(self.__game.someone_has_money() and self.__game.get_ai_players()[0].get_money() < self.__money_goal):
      self.__game.finish_round()
      hand_count += 1
      if highest_money < self.__game.get_ai_players()[0].get_money():
        highest_money = self.__game.get_ai_players()[0].get_money()

    simulation_time = round(time.time() - start_time, 2)
    ending_money = round(self.__game.get_ai_players()[0].get_money(), 0)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    human_time = f"{round(hand_count / 60, 2)} hrs"   # Currently assumes 60 hands/hrs
    self.__results = {
      "ending_money": ending_money,
      "hand_count": hand_count,
      "highest_money": highest_money,
      "human_time": human_time,
      "simulation_time": simulation_time
    }

  def get_results(self) -> SimulationResults:
    return self.__results

  def _get_bet(self) -> int:
    # TODO: Implement use of bet spread
    return 50
