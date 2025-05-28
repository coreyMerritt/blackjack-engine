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
    previous_money = self.__game.get_ai_players()[0].get_money()
    win_count = 0
    loss_count = 0
    draw_count = 0

    while(self.__game.someone_has_money() and self.__game.get_ai_players()[0].get_money() < self.__money_goal):
      previous_money = self.__game.get_ai_players()[0].get_money()
      self.__game.finish_round()
      hand_count += 1
      money = self.__game.get_ai_players()[0].get_money()

      if highest_money < money:
        highest_money = money

      if money > previous_money:
        win_count += 1
      elif money < previous_money:
        loss_count += 1
      else:
        draw_count += 1

      runtime = time.time() - start_time
      if runtime > 60:
        break

    simulation_time = round(time.time() - start_time, 2)
    ending_money = round(self.__game.get_ai_players()[0].get_money(), 0)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    human_time = f"{round(hand_count / 60, 2)} hrs"   # Currently assumes 60 hands/hrs
    self.__results = {
      "win_count": win_count,
      "loss_count": loss_count,
      "draw_count": draw_count,
      "win_ratio": f"{round((win_count / (win_count + loss_count)) * 100, 2)}%",
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
