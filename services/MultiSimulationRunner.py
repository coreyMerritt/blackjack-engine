import time
from typing import List
import cProfile
import pstats
import io
from entities.Game import Game
from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.core.HumanTime import HumanTime
from models.core.MultiSimBounds import MultiSimBounds
from models.core.SingleSimBounds import SingleSimBounds
from models.core.results.SimulationMultiResults import SimulationMultiResults
from models.core.results.SimulationMultiResultsFormatted import SimulationMultiResultsFormatted
from models.core.results.SimulationMultiResultsMetadata import SimulationMultiResultsMetadata
from models.core.results.SimulationSingleResults import SimulationSingleResults
from services.SimulationDataTransformer import SimulationDataTransformer
from services.SingleSimulationRunner import SingleSimulationRunner
import services.MathHelper as MathHelper


class MultiSimulationRunner():
  __simulation_data_transformer: SimulationDataTransformer
  __human_time_limit: int | None
  __sim_time_limit: int | None
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __results_progress: int
  __start_time: float | None
  __results: SimulationMultiResults

  def __init__(
    self,
    multi_bounds: MultiSimBounds,
    game: Game,
    bounds: SingleSimBounds,
    human_time: HumanTime,
    original_req: CreateMultiSimReq
  ):
    self.__simulation_data_transformer = SimulationDataTransformer()
    single_sim_req = self.__simulation_data_transformer.get_single_sim_req(original_req)
    self.__single_sim_runner = SingleSimulationRunner(game, bounds, human_time, single_sim_req)
    self.__human_time_limit = multi_bounds.human_time_limit
    self.__sim_time_limit = multi_bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__results_progress = 0
    self.__results = SimulationMultiResults.model_validate({})

  async def run(self, runs: int) -> None:
    self.__full_reset()
    single_sim_results = []
    metadata = SimulationMultiResultsMetadata.model_validate({})
    self.__start_time = time.time()

    for _ in range(0, runs):
      self.__single_sim_runner.reset_game()
      await self.__single_sim_runner.run(True)
      single_sim_results.append(self.__single_sim_runner.get_results())
      self.__count_sim(metadata)
      self.__update_results_progress(single_sim_results, metadata, runs)
      if self.__results_progress == 100:
        break

    end_time = time.time()
    metadata.success_rate = MathHelper.get_percentage(metadata.sims_won, metadata.sims_run)
    metadata.risk_of_ruin = MathHelper.get_percentage(metadata.sims_lost, metadata.sims_run)
    metadata.time_taken = end_time - self.__start_time
    self.__set_results(single_sim_results, metadata)

  async def run_with_benchmarking(self, runs: int) -> None:
    pr = cProfile.Profile()
    pr.enable()
    await self.run(runs)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    print(s.getvalue())

  def get_results(self) -> SimulationMultiResults | None:
    if not self.__results:
      return None
    return self.__results

  def get_results_formatted(self) -> SimulationMultiResultsFormatted | None:
    if not self.__results:
      return None
    formatted_results = self.__simulation_data_transformer.format_multi_sim_results(
      self.__results,
      self.__hours_per_day,
      self.__days_per_week
    )
    return formatted_results

  def get_results_progress(self) -> int:
    return self.__results_progress

  def __get_human_time(self, total_hands_played: int) -> float:
    return MathHelper.get_human_time(total_hands_played, self.__hands_per_hour)

  def __create_multi_sim_results(
    self,
    metadata: SimulationMultiResultsMetadata,
    single_sim_results: List[SimulationSingleResults]
  ) -> SimulationMultiResults:
    total_runs = len(single_sim_results)
    single_sims_summed = self.__simulation_data_transformer.get_single_sims_summed(single_sim_results)
    single_sims_averaged = self.__simulation_data_transformer.get_single_sims_averaged(single_sims_summed, total_runs)
    multi_sim_results = SimulationMultiResults.model_construct(
      metadata=metadata,
      sum=single_sims_summed,
      average=single_sims_averaged
    )
    return multi_sim_results

  def __set_results(
    self, single_sim_results: List[SimulationSingleResults],
    metadata: SimulationMultiResultsMetadata
  ) -> None:
    total_runs = len(single_sim_results)
    if total_runs == 0:
      return
    single_sims_summed = self.__simulation_data_transformer.get_single_sims_summed(single_sim_results)
    single_sims_averaged = self.__simulation_data_transformer.get_single_sims_averaged(single_sims_summed, total_runs)
    profit_from_true = float(sum(single_sims_averaged.bankroll.profit_from_true))
    total_profit = getattr(single_sims_averaged.bankroll, "total_profit")
    assert abs(profit_from_true - total_profit) < 0.01
    multi_sim_results = self.__create_multi_sim_results(metadata, single_sim_results)
    self.__results = multi_sim_results

  def __count_sim(self, metadata: SimulationMultiResultsMetadata) -> None:
    ending_bankroll = self.__single_sim_runner.get_bankroll()
    bankroll_goal = self.__single_sim_runner.get_bankroll_goal()
    metadata.sims_run += 1
    if ending_bankroll >= bankroll_goal:
      metadata.sims_won += 1
    elif ending_bankroll <= 0:
      metadata.sims_lost += 1
    else:
      metadata.sims_unfinished += 1

  def __full_reset(self) -> None:
    self.__results_progress = 0
    self.__results = SimulationMultiResults.model_validate({})
    self.__start_time = None

  def __update_results_progress(
    self,
    single_sim_results: List[SimulationSingleResults],
    metadata: SimulationMultiResultsMetadata,
    runs: int
  ) -> None:
    if self.__start_time is None:
      raise RuntimeError("start_time is None.")

    sim_time_percentage_done = 0
    if self.__sim_time_limit:
      time_elapsed = time.time() - self.__start_time
      sim_time_percentage_done = MathHelper.get_percentage(time_elapsed, self.__sim_time_limit)
      if sim_time_percentage_done > 100:
        sim_time_percentage_done = 100

    human_time_percentage_done = 0
    if self.__human_time_limit:
      total_hands_played = 0
      for result in single_sim_results:
        total_hands_played += result.hands.counts.total
      human_time = self.__get_human_time(total_hands_played)
      human_time_percentage_done = MathHelper.get_percentage(human_time, self.__human_time_limit)
      if human_time_percentage_done > 100:
        human_time_percentage_done = 100

    sim_count_percentage_done = MathHelper.get_percentage(metadata.sims_run, runs)
    highest_progress = max(sim_time_percentage_done, human_time_percentage_done, sim_count_percentage_done)
    highest_progress = min(highest_progress, 100)
    self.__results_progress = int(highest_progress)
    return
