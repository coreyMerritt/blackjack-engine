import os
import time
import asyncio
from typing import List
import cProfile
import pstats
import io
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from entities.Game import Game
from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.HumanTime import HumanTime
from models.core.MultiSimBounds import MultiSimBounds
from models.core.SingleSimBounds import SingleSimBounds
from models.core.results.SimMultiResults import SimMultiResults
from models.core.results.SimMultiResultsFormatted import SimMultiResultsFormatted
from models.core.results.SimMultiResultsMetadata import SimMultiResultsMetadata
from models.core.results.SimSingleResults import SimSingleResults
from services.DatabaseHandler import DatabaseHandler
from services.SimDataTransformer import SimDataTransformer
from services.SingleSimRunner import SingleSimRunner
import services.MathHelper as MathHelper


class MultiSimRunner():
  __database_handler: DatabaseHandler
  __simulation_data_transformer: SimDataTransformer
  __human_time_limit: int | None
  __sim_time_limit: int | None
  __hands_per_hour: int
  __hours_per_day: int
  __days_per_week: int
  __results_progress: int
  __start_time: float | None
  __results: SimMultiResults

  def __init__(
    self,
    multi_bounds: MultiSimBounds,
    game: Game,
    bounds: SingleSimBounds,
    human_time: HumanTime,
    original_req: CreateMultiSimReq
  ):
    self.__database_handler = DatabaseHandler()
    self.__simulation_data_transformer = SimDataTransformer()
    single_sim_req = self.__simulation_data_transformer.get_single_sim_req(original_req)
    self.__single_sim_runner = SingleSimRunner(game, bounds, human_time, single_sim_req)
    self.__human_time_limit = multi_bounds.human_time_limit
    self.__sim_time_limit = multi_bounds.sim_time_limit
    self.__hands_per_hour = human_time.hands_per_hour
    self.__hours_per_day = human_time.hours_per_day
    self.__days_per_week = human_time.days_per_week
    self.__results_progress = 0
    self.__results = SimMultiResults.model_validate({})

  async def run(self, runs: int) -> None:
    self.__full_reset()
    self.__start_time = time.time()

    loop = asyncio.get_running_loop()
    req = self.__single_sim_runner.get_original_req()
    req_dict = req.model_dump()

    num_workers = os.cpu_count() or 2
    metadata = SimMultiResultsMetadata.model_validate({})
    results: List[SimSingleResults] = []

    completed_runs = 0
    lock = asyncio.Lock()

    executor = ProcessPoolExecutor(max_workers=os.cpu_count())

    async def worker():
      nonlocal completed_runs
      while True:
        async with lock:
          if completed_runs >= runs:
            break
          completed_runs += 1
        res = await loop.run_in_executor(executor, MultiSimRunner.run_one_sync_sim, req_dict)
        results.append(res)
        self.__count_sim(metadata, res)
        self.__update_results_progress(results, metadata, runs)

    await asyncio.gather(*(worker() for _ in range(min(num_workers, runs))))
    executor.shutdown()

    end_time = time.time()
    metadata.success_rate = MathHelper.get_percentage(
      metadata.sims_won,
      (metadata.sims_run - metadata.sims_unfinished)
    )
    metadata.failure_rate = MathHelper.get_percentage(
      metadata.sims_lost,
      (metadata.sims_run - metadata.sims_unfinished)
    )
    print(metadata.success_rate + metadata.failure_rate)
    assert metadata.success_rate + metadata.failure_rate == 100.0
    single_sim_results_summed = self.__simulation_data_transformer.get_single_sims_summed(results)
    metadata.total_hands = single_sim_results_summed.hands.counts.total
    metadata.simulation_time = end_time - self.__start_time
    metadata.human_time = self.__get_human_time(metadata.total_hands)

    self.__set_results(results, metadata)
    with ThreadPoolExecutor(max_workers=10) as executor:
      futures = [
        loop.run_in_executor(executor, self.__database_handler.store_simulation_single_result, r, req)
        for r in results
      ]
      await asyncio.gather(*futures)

  @staticmethod
  def run_one_sync_sim(req_dict: dict) -> SimSingleResults:
    req = CreateSingleSimReq(**req_dict)
    game = Game(req.rules, req.ai_player_info)
    runner = SingleSimRunner(game, req.bounds, req.time, req)
    runner.run_sync()
    return runner.get_results()

  async def run_with_one_core(self, runs: int) -> None:
    self.__full_reset()
    single_sim_results = []
    metadata = SimMultiResultsMetadata.model_validate({})
    self.__start_time = time.time()

    for _ in range(0, runs):
      self.__single_sim_runner.reset_game()
      await self.__single_sim_runner.run()
      single_sim_results.append(self.__single_sim_runner.get_results())
      self.__count_sim_one_core(metadata)
      self.__update_results_progress(single_sim_results, metadata, runs)
      if self.__results_progress == 100:
        break

    end_time = time.time()
    metadata.success_rate = MathHelper.get_percentage(
      metadata.sims_won,
      (metadata.sims_run - metadata.sims_unfinished)
    )
    metadata.failure_rate = MathHelper.get_percentage(
      metadata.sims_lost,
      (metadata.sims_run - metadata.sims_unfinished)
    )
    print(metadata.success_rate + metadata.failure_rate)
    assert metadata.success_rate + metadata.failure_rate == 100.0
    time_taken = end_time - self.__start_time
    single_sim_results_summed = self.__simulation_data_transformer.get_single_sims_summed(single_sim_results)
    metadata.total_hands = single_sim_results_summed.hands.counts.total
    metadata.simulation_time = time_taken
    metadata.human_time = self.__get_human_time(single_sim_results_summed.hands.counts.total)
    self.__set_results(single_sim_results, metadata)

  async def run_with_benchmarking(self, runs: int) -> None:
    pr = cProfile.Profile()
    pr.enable()
    await self.run_with_one_core(runs)
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
    ps.print_stats(30)
    print(s.getvalue())

  def get_results(self) -> SimMultiResults | None:
    if not self.__results:
      return None
    return self.__results

  def get_results_formatted(self) -> SimMultiResultsFormatted | None:
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
    metadata: SimMultiResultsMetadata,
    single_sim_results: List[SimSingleResults]
  ) -> SimMultiResults:
    total_runs = len(single_sim_results)
    single_sims_summed = self.__simulation_data_transformer.get_single_sims_summed(single_sim_results)
    single_sims_averaged = self.__simulation_data_transformer.get_single_sims_averaged(single_sims_summed, total_runs)
    multi_sim_results = SimMultiResults.model_construct(
      metadata=metadata,
      average=single_sims_averaged
    )
    return multi_sim_results

  def __set_results(
    self, single_sim_results: List[SimSingleResults],
    metadata: SimMultiResultsMetadata
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

  def __count_sim(self, metadata: SimMultiResultsMetadata, result: SimSingleResults) -> None:
    ending_bankroll = result.bankroll.ending
    bankroll_goal = self.__single_sim_runner.get_bankroll_goal()
    bankroll_fail = self.__single_sim_runner.get_bankroll_fail()
    metadata.sims_run += 1
    if ending_bankroll >= bankroll_goal:
      metadata.sims_won += 1
    elif ending_bankroll <= bankroll_fail:
      metadata.sims_lost += 1
    else:
      metadata.sims_unfinished += 1

  def __count_sim_one_core(self, metadata: SimMultiResultsMetadata) -> None:
    ending_bankroll = self.__single_sim_runner.get_bankroll()
    bankroll_goal = self.__single_sim_runner.get_bankroll_goal()
    bankroll_fail = self.__single_sim_runner.get_bankroll_fail()
    metadata.sims_run += 1
    if ending_bankroll >= bankroll_goal:
      metadata.sims_won += 1
    elif ending_bankroll <= bankroll_fail:
      metadata.sims_lost += 1
    else:
      metadata.sims_unfinished += 1

  def __full_reset(self) -> None:
    self.__results_progress = 0
    self.__results = SimMultiResults.model_validate({})
    self.__start_time = None

  def __update_results_progress(
    self,
    single_sim_results: List[SimSingleResults],
    metadata: SimMultiResultsMetadata,
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
