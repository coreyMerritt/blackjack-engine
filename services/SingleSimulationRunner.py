import asyncio
from cmath import inf
from copy import deepcopy
import os
import time
from typing import List
from entities.Game import Game
from entities.Hand import Hand
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds
from models.core.results.SimulationSingleResultsFormatted import SimulationSingleResultsFormatted
from models.core.results.SimulationSingleResults import SimulationSingleResults
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult
from services.BlackjackLogger import BlackjackLogger


class SingleSimulationRunner():
  __bankroll_goal: int
  __human_time_limit: int
  __sim_time_limit: int
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __results_progress: int
  __start_time: float | None
  __game: Game
  __game_starting_point: Game
  __results: SimulationSingleResults

  def __init__(self, game: Game, bounds: SingleSimBounds, human_time: HumanTime):
    if bounds.bankroll_goal is None:
      self.__bankroll_goal = inf
    else:
      self.__bankroll_goal = bounds.bankroll_goal
    self.__human_time_limit = bounds.human_time_limit
    self.__sim_time_limit = bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__results_progress = 0
    self.__game = game
    self.__game_starting_point = deepcopy(game)
    self.__results = None

  async def run(self, called_from_multi=False) -> None:
    if not called_from_multi:
      self.__full_reset()
    self.__start_time = time.time()
    br = self.__game.get_ai_players()[0].get_bankroll()
    bankroll = {"starting": br, "highest": br, "lowest": br}
    counts = {"total": 0, "won": 0, "lost": 0, "drawn": 0, "blackjack": 0, "surrendered": 0}
    profit_from_true = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    someone_has_bankroll = self.__game.someone_has_bankroll()
    bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()
    assert self.get_bankroll_goal() > self.__game.get_ai_players()[0].get_bankroll()

    while(someone_has_bankroll and bankroll_is_below_goal):
      await self.__play_a_hand(bankroll, profit_from_true, counts)
      assert self.__results_progress <= 100
      assert self.__results_progress >= -100
      if self.__results_progress == 100 or self.__results_progress == -100:
        break
      someone_has_bankroll = self.__game.someone_has_bankroll()
      bankroll_is_below_goal = self.__calculate_if_bankroll_is_below_goal()

    ending_bankroll = self.__game.get_ai_players()[0].get_bankroll()
    assert ending_bankroll >= 0
    max_possible_win = self.__game.get_ai_players()[0].get_bet_spread().true_six * 8
    assert ending_bankroll <= self.__bankroll_goal + max_possible_win
    total_profit = ending_bankroll - bankroll["starting"]
    percentages = {
      "blackjack": self.__get_blackjack_rate(counts),
      "won": self.__get_win_rate(counts),
      "drawn": self.__get_draw_rate(counts),
      "lost": self.__get_loss_rate(counts),
      "surrendered": self.__get_surrender_rate(counts)
    }
    assert sum(percentages.values()) >= 99.99
    assert sum(percentages.values()) <= 100.01

    self.__results = {
      "hands": {
        "counts": counts,
        "percentages": percentages
      },
      "bankroll": {
        "starting": bankroll["starting"],
        "ending": ending_bankroll,
        "total_profit": total_profit,
        "profit_from_true": profit_from_true,
        "profit_per_hand": total_profit / counts["total"],
        "profit_per_hour": (total_profit / counts["total"]) * self.__hands_per_hour,
        "peak": bankroll["highest"]
      },
      "time": {
        "human_time": self.__get_human_time(counts["total"]),
        "simulation_time": time.time() - self.__start_time
      }
    }

  def get_bankroll_goal(self) -> float:
    return self.__bankroll_goal

  def get_bankroll(self) -> float:
    return self.__game.get_ai_players()[0].get_bankroll()

  def get_results_progress(self) -> int:
    return self.__results_progress

  def get_results(self) -> SimulationSingleResults | None:
    if self.__results is None:
      return None
    return self.__results

  def get_results_formatted(self) -> SimulationSingleResultsFormatted:
    if not self.__results:
      return None

    return {
      "hands": {
        "counts": {
          "total": f"{int(self.__results['hands']['counts']['total']):,}",
          "blackjack": f"{int(self.__results['hands']['counts']['blackjack']):,}",
          "won": f"{int(self.__results['hands']['counts']['won']):,}",
          "drawn": f"{int(self.__results['hands']['counts']['drawn']):,}",
          "lost": f"{int(self.__results['hands']['counts']['lost']):,}",
          "surrendered": f"{int(self.__results['hands']['counts']['surrendered']):,}"
        },
        "percentages": {
          "blackjack": f"{round(self.__results['hands']['percentages']['blackjack'], 2):.2f}%",
          "won": f"{round(self.__results['hands']['percentages']['won'], 2):.2f}%",
          "drawn": f"{round(self.__results['hands']['percentages']['drawn'], 2):.2f}%",
          "lost": f"{round(self.__results['hands']['percentages']['lost'], 2):.2f}%",
          "surrendered": f"{round(self.__results['hands']['percentages']['surrendered'], 2):.2f}%"
        }
      },
      "bankroll": {
        "starting": self.__get_formatted_bankroll(self.__results["bankroll"]["starting"]),
        "ending": self.__get_formatted_bankroll(self.__results["bankroll"]["ending"]),
        "total_profit": self.__get_formatted_bankroll(self.__results["bankroll"]["total_profit"]),
        "profit_from_true": {
          0: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][0]),
          1: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][1]),
          2: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][2]),
          3: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][3]),
          4: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][4]),
          5: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][5]),
          6: self.__get_formatted_bankroll(self.__results["bankroll"]["profit_from_true"][6])
        },
        "profit_per_hand": self.__get_formatted_bankroll(self.__results["bankroll"]["profit_per_hand"]),
        "profit_per_hour": self.__get_formatted_bankroll(self.__results["bankroll"]["profit_per_hour"]),
        "peak": self.__get_formatted_bankroll(self.__results["bankroll"]["peak"])
      },
      "time": {
        "human_time": self.__get_time_formatted(self.__results["time"]["human_time"]),
        "simulation_time": self.__get_time_formatted(self.__results["time"]["simulation_time"])
      }
    }

  def set_results(self, results: SimulationSingleResults) -> None:
    self.__results = results

  def reset_game(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)

  def __calculate_if_bankroll_is_below_goal(self) -> bool:
    if self.__bankroll_goal:
      return self.__game.get_ai_players()[0].get_bankroll() < self.__bankroll_goal
    else:
      return True

  def __get_human_time(self, total_hands_played: int) -> float:
    hours = total_hands_played / self.__hands_per_hour
    minutes = hours * 60
    seconds = minutes * 60
    return seconds

  def __get_blackjack_rate(self, counts: dict) -> float:
    return (counts["blackjack"] / counts["total"]) * 100

  def __get_win_rate(self, counts: dict) -> float:
    return (counts["won"] / counts["total"]) * 100

  def __get_draw_rate(self, counts: dict) -> float:
    return (counts["drawn"] / counts["total"]) * 100

  def __get_loss_rate(self, counts: dict) -> float:
    return (counts["lost"] / counts["total"]) * 100

  def __get_surrender_rate(self, counts: dict) -> float:
    return (counts["surrendered"] / counts["total"]) * 100

  def __get_formatted_bankroll(self, bankroll: float) -> str:
    return f"-${abs(bankroll):,.2f}" if bankroll < 0 else f"${bankroll:,.2f}"

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

  def __full_reset(self) -> None:
    self.__game = deepcopy(self.__game_starting_point)
    self.__results_progress = 0
    self.__results = None

  async def __play_a_hand(self, bankroll: dict, profit_from_true: dict, counts: dict) -> None:
    ai_player = self.__game.get_ai_players()[0]
    true_count = ai_player.calculate_true_count(self.__game.get_dealer().get_decks_remaining())
    self.__game.continue_until_state(GameState.CLEANUP)
    assert self.__game.get_state() == GameState.CLEANUP
    self.__update_bankroll(bankroll)
    for hand in ai_player.get_hands():
      self.__update_profits(hand, true_count, profit_from_true, counts)
    total_profit = ai_player.get_bankroll() - bankroll["starting"]
    total_from_true = sum(profit_from_true)
    assert abs(total_profit - total_from_true) < 0.01
    self.__game.finish_round()
    assert self.__game.get_state() == GameState.BETTING
    await self.__occasionally_yield_event_loop_control(counts["total"])
    self.__update_results_progress(counts["total"], time.time() - self.__start_time)

  async def __occasionally_yield_event_loop_control(self, total_hands_played) -> None:
    if total_hands_played % int(os.getenv('BJE_YIELD_EVERY_X_HANDS')) == 0:
      await asyncio.sleep(0)

  def __update_bankroll(self, bankroll: dict) -> None:
    current_player_bankroll = self.__game.get_ai_players()[0].get_bankroll()
    if bankroll["highest"] < current_player_bankroll:
      bankroll["highest"] = current_player_bankroll
    if bankroll["lowest"] > current_player_bankroll:
      bankroll["lowest"] = current_player_bankroll

  def __update_profits(self, hand: Hand, true_count: int, profit_from_true: List[float], counts: dict) -> None:
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
      counts["blackjack"] += 1
    elif hand_result == HandResult.WIN:
      counts["won"] += 1
    elif hand_result == HandResult.LOSS:
      profit_from_true[adjusted_true_count] -= bet
      counts["lost"] += 1
    elif hand_result == HandResult.DRAW:
      counts["drawn"] += 1
    elif hand_result == HandResult.SURRENDERED:
      profit_from_true[adjusted_true_count] -= bet / 2
      counts["surrendered"] += 1
    counts["total"] += 1
    BlackjackLogger.debug(f"\t\tHand result: {hand_result}")
    BlackjackLogger.debug(f"\t\tPayout: {payout}")

  def __update_results_progress(self, total_hands_played: int, time_elapsed_seconds: float) -> None:
    if self.__human_time_limit is not None:
      human_seconds = self.__get_human_time(total_hands_played)
      human_time_progress = int(human_seconds / self.__human_time_limit) * 100
      self.__results_progress = min(human_time_progress, 100)
      return

    if self.__sim_time_limit is not None:
      sim_time_progress = int(time_elapsed_seconds / self.__sim_time_limit)
      self.__results_progress = min(sim_time_progress, 100)
      return

    if self.__bankroll_goal != inf:
      bankroll_after_round = self.__game.get_ai_players()[0].get_bankroll()
      if bankroll_after_round == 0:
        self.__results_progress = -100
        return
      else:
        winning_progress = int(((bankroll_after_round / self.__bankroll_goal) * 200) - 100)
        winning_progress = max(-100, min(100, winning_progress))
        self.__results_progress = winning_progress
        return

    self.__results_progress = 0
    return
