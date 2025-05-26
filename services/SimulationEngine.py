import time
from entities.Game import Game
from models.core.BetSpread import BetSpread
from models.api.SimulationResultsRes import SimulationResults
from models.enums.GameState import GameState
from services.BlackjackEngine import BlackjackEngine


class SimulationEngine():
  money_goal: int
  game: Game
  bet_spread: BetSpread
  results: SimulationResults

  def __init__(self, game: Game, bet_spread: BetSpread, money_goal: int) -> None:
    self.money_goal = money_goal
    self.game = game
    self.bet_spread = bet_spread

  def run(self) -> None:
    start_time = time.time()
    hand_count = 0
    highest_money = self.game.ai_players[0].money

    while(self.game.ai_players[0].money > 0 and self.game.ai_players[0].money < self.money_goal):
      self.run_core_gameplay_loop()
      hand_count += 1
      if highest_money < self.game.ai_players[0].money:
        highest_money = self.game.ai_players[0].money

    simulation_time = round(time.time() - start_time, 2)
    ending_money = round(self.game.ai_players[0].money, 0)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    human_time = f"{round(hand_count / 60, 2)} hrs"   # Currently assumes 60 hands/hrs
    self.results = {
      "ending_money": ending_money,
      "hand_count": hand_count,
      "highest_money": highest_money,
      "human_time": human_time,
      "simulation_time": simulation_time
    }

  def run_core_gameplay_loop(self) -> None:
    self.game.state = GameState.BETTING
    current_bet = self._get_bet()
    self.game.place_bets(current_bet)

    self.game.state = GameState.DEALING
    self.game.deal_cards()
    self.game.finish_round()

  def get_results(self) -> SimulationResults:
    return self.results

  def _get_bet(self) -> int:
    # TODO: Implement use of bet spread
    return 50
