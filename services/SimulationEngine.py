import time
from entities.Game import Game
from models.api.BetSpread import BetSpread
from models.api.SimulationResultsRes import SimulationResults
from models.enums.GameState import GameState


class SimulationEngine():
  win_value: int
  game: Game
  bet_spread: BetSpread
  results: SimulationResults

  def __init__(self, game: Game, bet_spread: BetSpread, win_value: int) -> None:
    self.win_value = win_value
    self.game = game
    self.bet_spread = bet_spread

  def run(self) -> None:
    start_time = time.time()
    hand_count = 0
    highest_money = self.game.players[0].money

    while(self.game.players[0].money > 0 and self.game.players[0].money < self.win_value):
      self.game.state = GameState.BETTING
      current_bet = self._get_bet()
      self.game.place_bet(current_bet)

      self.game.state = GameState.DEALING
      self.game.deal_cards()

      self.game.state = GameState.HUMAN_PLAYER_DECISIONS
      if self.game.players[0].get_hand_value() < 21:
        self._handle_decisions()
      self.game.finish_round()

      hand_count += 1
      if highest_money < self.game.players[0].money:
        highest_money = self.game.players[0].money

    simulation_time = round(time.time() - start_time, 2)
    ending_money = round(self.game.players[0].money, 0)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    human_time = f"{round(hand_count / 60, 2)} hrs"
    self.results = {
      "ending_money": ending_money,
      "hand_count": hand_count,
      "highest_money": highest_money,
      "human_time": human_time,
      "simulation_time": simulation_time
    }

  def get_results(self):
    return self.results

  def _get_bet(self):
    # TODO: Implement use of bet spread
    return 50

  def _handle_decisions(self):
    # TODO: Implement some real decision making
    while self.game.players[0].get_hand_value() < 17:
      self.game.hit()
