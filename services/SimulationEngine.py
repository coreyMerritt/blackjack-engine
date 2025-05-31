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
from services.BlackjackLogger import BlackjackLogger


class SimulationEngine():
  __bankroll_goal: int
  __sim_time_limit: int
  __human_time_limit: int
  __multi_start_time: float | None
  __game: Game
  __game_starting_point: Game
  __single_results: SimulationSingleResults
  __single_results_status: int
  __multi_results: SimulationMultiResults
  __multi_results_status: int

  def __init__(self, game: Game, bankroll_goal: int, human_time_limit: int | None, sim_time_limit: int | None):
    self.__bankroll_goal = bankroll_goal
    self.__human_time_limit = human_time_limit
    self.__sim_time_limit = sim_time_limit
    self.__multi_start_time = None
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
    sims_unfinished = 0
    self.__multi_start_time = time.time()
    for _ in range(0, runs):
      self.reset_game()
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
      self.__multi_results_status = int((sims_run / runs) * 100)

      if self.__sim_time_limit:
        if time.time() - self.__multi_start_time > self.__sim_time_limit:
          self.__multi_results_status = 100
          break

      if self.__human_time_limit:
        total_hands_played = 0
        for result in results:
          total_hands_played += result["total_hands_played"]
        human_time = self.__get_human_time(total_hands_played)
        if human_time > self.__human_time_limit:
          self.__multi_results_status = 100
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

  async def run(self, called_from_multi=False) -> None:
    if not called_from_multi:
      self.full_reset()
    start_time = time.time()
    (starting_bankroll, highest_bankroll) = (self.__game.get_ai_players()[0].get_bankroll(),) * 2
    (hands_won_count, hands_lost_count, hands_drawn_count, blackjack_count,
    profit_from_true_zero, profit_from_true_one, profit_from_true_two, profit_from_true_three,
    profit_from_true_four, profit_from_true_five, profit_from_true_six) = (0,) * 11

    while(self.__game.someone_has_bankroll() and self.__game.get_ai_players()[0].get_bankroll() < self.__bankroll_goal):
      self.__game.continue_until_state(GameState.PAYOUTS)
      bankroll = self.__game.get_ai_players()[0].get_bankroll()
      if highest_bankroll < bankroll:
        highest_bankroll = bankroll
      for player in self.__game.get_human_and_ai_players():
        bet_spread = player.get_bet_spread()
        for hand in player.get_hands():
          hand_result = hand.get_result()
          bet = hand.get_bet()
          initial_bet = hand.get_initial_bet()
          BlackjackLogger.debug(f"\t\tBet history: {initial_bet}")
          payout = 0
          if hand_result == HandResult.BLACKJACK:
            payout = bet * self.__game.get_dealer().get_blackjack_pays_multiplier()
            match initial_bet:
              case bet_spread.true_zero:
                profit_from_true_zero += payout
              case bet_spread.true_one:
                profit_from_true_one += payout
              case bet_spread.true_two:
                profit_from_true_two += payout
              case bet_spread.true_three:
                profit_from_true_three += payout
              case bet_spread.true_four:
                profit_from_true_four += payout
              case bet_spread.true_five:
                profit_from_true_five += payout
              case bet_spread.true_six:
                profit_from_true_six += payout
            blackjack_count += 1
            hands_won_count += 1
          elif hand_result == HandResult.WIN:
            payout = bet
            match initial_bet:
              case bet_spread.true_zero:
                profit_from_true_zero += payout
              case bet_spread.true_one:
                profit_from_true_one += payout
              case bet_spread.true_two:
                profit_from_true_two += payout
              case bet_spread.true_three:
                profit_from_true_three += payout
              case bet_spread.true_four:
                profit_from_true_four += payout
              case bet_spread.true_five:
                profit_from_true_five += payout
              case bet_spread.true_six:
                profit_from_true_six += payout
            hands_won_count += 1
          elif hand_result == HandResult.LOSS:
            payout = -(bet)
            match initial_bet:
              case bet_spread.true_zero:
                profit_from_true_zero += payout
              case bet_spread.true_one:
                profit_from_true_one += payout
              case bet_spread.true_two:
                profit_from_true_two += payout
              case bet_spread.true_three:
                profit_from_true_three += payout
              case bet_spread.true_four:
                profit_from_true_four += payout
              case bet_spread.true_five:
                profit_from_true_five += payout
              case bet_spread.true_six:
                profit_from_true_six += payout
            hands_lost_count += 1
          elif hand_result == HandResult.DRAW:
            payout = 0
            hands_drawn_count += 1
          BlackjackLogger.debug(f"\t\tHand result: {hand_result}")
          if payout:
            BlackjackLogger.debug(f"\t\tPayout: {payout}")
      self.__game.finish_round()
      total_hands_played = hands_won_count + hands_lost_count + hands_drawn_count
      bankroll_after_round = self.__game.get_ai_players()[0].get_bankroll()
      if bankroll_after_round == 0:
        self.__single_results_status = 100
      else:
        winning_progress = int((bankroll_after_round / self.__bankroll_goal) * 100)
        losing_progress = int(((starting_bankroll - bankroll_after_round) / starting_bankroll) * 100)
        self.__single_results_status = max(winning_progress, losing_progress)

      if total_hands_played % 100 == 0:
        await asyncio.sleep(0)

      if self.__sim_time_limit:
        if self.__multi_start_time:
          if time.time() - self.__multi_start_time > self.__sim_time_limit:
            self.__single_results_status = 100
            break
        else:
          if time.time() - start_time > self.__sim_time_limit:
            self.__single_results_status = 100
            break

      if self.__human_time_limit:
        human_time = self.__get_human_time(total_hands_played)
        if human_time > self.__human_time_limit:
          self.__single_results_status = 100
          break

    simulation_time = round(time.time() - start_time, 2)
    total_hands_played = hands_won_count + hands_lost_count + hands_drawn_count
    hands_won_percent = (hands_won_count / total_hands_played) * 100
    hands_lost_percent = (hands_lost_count / total_hands_played) * 100
    hands_drawn_percent = (hands_drawn_count / total_hands_played) * 100
    ending_bankroll = round(self.__game.get_ai_players()[0].get_bankroll(), 0)
    total_profit = round(ending_bankroll - starting_bankroll, 2)
    profit_from_true_zero = round(profit_from_true_zero, 2)
    profit_from_true_one = round(profit_from_true_one, 2)
    profit_from_true_two = round(profit_from_true_two, 2)
    profit_from_true_three = round(profit_from_true_three, 2)
    profit_from_true_four = round(profit_from_true_four, 2)
    profit_from_true_five = round(profit_from_true_five, 2)
    profit_from_true_six = round(profit_from_true_six, 2)
    profit_per_hand = round(total_profit / total_hands_played, 2)
    profit_per_hour = round(profit_per_hand * 60, 2)
    # TODO: Modularize the human_time -- allow user to define how long an average hand takes
    human_time = self.__get_human_time(total_hands_played)
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
      "bankroll": {
        "starting": starting_bankroll,
        "ending": ending_bankroll,
        "total_profit": total_profit,
        "profit_from_true": {
          "zero": profit_from_true_zero,
          "one": profit_from_true_one,
          "two": profit_from_true_two,
          "three": profit_from_true_three,
          "four": profit_from_true_four,
          "five": profit_from_true_five,
          "six": profit_from_true_six
        },
        "profit_per_hand": profit_per_hand,
        "profit_per_hour": profit_per_hour,
        "peak": highest_bankroll
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
    starting_bankroll = float(self.__single_results["bankroll"]["starting"])
    ending_bankroll = float(self.__single_results["bankroll"]["ending"])
    total_profit = float(self.__single_results["bankroll"]["total_profit"])
    profit_from_true_zero = float(self.__single_results["bankroll"]["profit_from_true"]["zero"])
    profit_from_true_one = float(self.__single_results["bankroll"]["profit_from_true"]["one"])
    profit_from_true_two = float(self.__single_results["bankroll"]["profit_from_true"]["two"])
    profit_from_true_three = float(self.__single_results["bankroll"]["profit_from_true"]["three"])
    profit_from_true_four = float(self.__single_results["bankroll"]["profit_from_true"]["four"])
    profit_from_true_five = float(self.__single_results["bankroll"]["profit_from_true"]["five"])
    profit_from_true_six = float(self.__single_results["bankroll"]["profit_from_true"]["six"])
    profit_per_hand = float(self.__single_results["bankroll"]["profit_per_hand"])
    profit_per_hour = float(self.__single_results["bankroll"]["profit_per_hour"])
    peak = float(self.__single_results["bankroll"]["peak"])
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
      "bankroll": {
        "starting": self.__format_bankroll(starting_bankroll),
        "ending": self.__format_bankroll(ending_bankroll),
        "total_profit": self.__format_bankroll(total_profit),
        "profit_from_true": {
          "zero": self.__format_bankroll(profit_from_true_zero),
          "one": self.__format_bankroll(profit_from_true_one),
          "two": self.__format_bankroll(profit_from_true_two),
          "three": self.__format_bankroll(profit_from_true_three),
          "four": self.__format_bankroll(profit_from_true_four),
          "five": self.__format_bankroll(profit_from_true_five),
          "six": self.__format_bankroll(profit_from_true_six)
        },
        "profit_per_hand": self.__format_bankroll(profit_per_hand),
        "profit_per_hour": self.__format_bankroll(profit_per_hour),
        "peak": self.__format_bankroll(peak)
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

  def __get_human_time(self, total_hands_played: int) -> float:
    hands_per_hour = 60
    hours = total_hands_played / hands_per_hour
    minutes = hours * 60
    seconds = minutes * 60
    human_time = round(seconds, 2)
    return human_time

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
      summed["hands_lost"]["count"] += int(r["hands_lost"]["count"])
      summed["hands_drawn"]["count"] += int(r["hands_drawn"]["count"])
      summed["bankroll"]["starting"] += float(r["bankroll"]["starting"])
      summed["bankroll"]["ending"] += float(r["bankroll"]["ending"])
      summed["bankroll"]["total_profit"] += float(r["bankroll"]["total_profit"])
      summed["bankroll"]["profit_from_true"]["zero"] += float(r["bankroll"]["profit_from_true"]["zero"])
      summed["bankroll"]["profit_from_true"]["one"] += float(r["bankroll"]["profit_from_true"]["one"])
      summed["bankroll"]["profit_from_true"]["two"] += float(r["bankroll"]["profit_from_true"]["two"])
      summed["bankroll"]["profit_from_true"]["three"] += float(r["bankroll"]["profit_from_true"]["three"])
      summed["bankroll"]["profit_from_true"]["four"] += float(r["bankroll"]["profit_from_true"]["four"])
      summed["bankroll"]["profit_from_true"]["five"] += float(r["bankroll"]["profit_from_true"]["five"])
      summed["bankroll"]["profit_from_true"]["six"] += float(r["bankroll"]["profit_from_true"]["six"])
      summed["bankroll"]["profit_per_hand"] += float(r["bankroll"]["profit_per_hand"])
      summed["bankroll"]["profit_per_hour"] += float(r["bankroll"]["profit_per_hour"])
      summed["bankroll"]["peak"] += float(r["bankroll"]["peak"])
      summed["time"]["human_time"] += float(r["time"]["human_time"])
      summed["time"]["simulation_time"] += float(r["time"]["simulation_time"])

    summed_hands_won = summed["hands_won"]["count"]
    summed_hands_lost = summed["hands_lost"]["count"]
    summed_hands_drawn = summed["hands_drawn"]["count"]
    summed_total_hands = summed["total_hands_played"]
    hands_won_percent = (summed_hands_won / summed_total_hands) * 100
    hands_lost_percent = (summed_hands_lost / summed_total_hands) * 100
    hands_drawn_percent = (summed_hands_drawn / summed_total_hands) * 100
    averaged = SimulationSingleResults().model_dump()
    averaged["total_hands_played"] = summed["total_hands_played"] // total_runs
    averaged["hands_won"]["count"] = summed["hands_won"]["count"] // total_runs
    averaged["hands_won"]["percent"] = hands_won_percent
    averaged["hands_lost"]["count"] = summed["hands_lost"]["count"] // total_runs
    averaged["hands_lost"]["percent"] = hands_lost_percent
    averaged["hands_drawn"]["count"] = summed["hands_drawn"]["count"] // total_runs
    averaged["hands_drawn"]["percent"] = hands_drawn_percent
    averaged["bankroll"]["starting"] = summed["bankroll"]["starting"] / total_runs
    averaged["bankroll"]["ending"] = summed["bankroll"]["ending"] / total_runs
    averaged["bankroll"]["total_profit"] = summed["bankroll"]["total_profit"] / total_runs
    averaged["bankroll"]["profit_from_true"]["zero"] = summed["bankroll"]["profit_from_true"]["zero"] / total_runs
    averaged["bankroll"]["profit_from_true"]["one"] = summed["bankroll"]["profit_from_true"]["one"] / total_runs
    averaged["bankroll"]["profit_from_true"]["two"] = summed["bankroll"]["profit_from_true"]["two"] / total_runs
    averaged["bankroll"]["profit_from_true"]["three"] = summed["bankroll"]["profit_from_true"]["three"] / total_runs
    averaged["bankroll"]["profit_from_true"]["four"] = summed["bankroll"]["profit_from_true"]["four"] / total_runs
    averaged["bankroll"]["profit_from_true"]["five"] = summed["bankroll"]["profit_from_true"]["five"] / total_runs
    averaged["bankroll"]["profit_from_true"]["six"] = summed["bankroll"]["profit_from_true"]["six"] / total_runs
    averaged["bankroll"]["profit_per_hand"] = summed["bankroll"]["profit_per_hand"] / total_runs
    averaged["bankroll"]["profit_per_hour"] = summed["bankroll"]["profit_per_hour"] / total_runs
    averaged["bankroll"]["peak"] = summed["bankroll"]["peak"] / total_runs
    averaged["time"]["human_time"] = summed["time"]["human_time"] / total_runs
    averaged["time"]["simulation_time"] = summed["time"]["simulation_time"] / total_runs

    multi_sim = SimulationMultiResults().model_dump()
    multi_sim["sims_run"] = sim_results["sims_run"]
    multi_sim["sims_won"] = sim_results["sims_won"]
    multi_sim["sims_lost"] = sim_results["sims_lost"]
    multi_sim["sims_unfinished"] = sim_results["sims_unfinished"]
    multi_sim["success_rate"] = sim_results["success_rate"]
    multi_sim["risk_of_ruin"] = sim_results["risk_of_ruin"]
    multi_sim["time_taken"] = sim_results["time_taken"]
    multi_sim["average"] = averaged
    self.__multi_results = multi_sim

  def __format_bankroll(self, value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"
