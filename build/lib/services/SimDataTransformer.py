from typing import List

from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.results.HandResultsCounts import HandResultsCounts
from models.core.results.HandResultsCountsFormatted import HandResultsCountsFormatted
from models.core.results.HandResultsPercentagesFormatted import HandResultsPercentagesFormatted
from models.core.results.HandResultsPercentages import HandResultsPercentages
from models.core.results.SimMultiResults import SimMultiResults
from models.core.results.SimMultiResultsFormatted import SimMultiResultsFormatted
from models.core.results.SimMultiResultsMetadata import SimMultiResultsMetadata
from models.core.results.SimMultiResultsMetadataFormatted import SimMultiResultsMetadataFormatted
from models.core.results.SimSingleResults import SimSingleResults
from models.core.results.ProfitResults import ProfitResults
from models.core.results.ProfitResultsFormatted import ProfitResultsFormatted
from models.core.results.BankrollResults import BankrollResults
from models.core.results.BankrollResultsFormatted import BankrollResultsFormatted
from models.core.results.HandResults import HandResults
from models.core.results.HandResultsFormatted import HandResultsFormatted
from models.core.results.SimSingleResultsFormatted import SimSingleResultsFormatted
from models.core.results.TimeResults import TimeResults
from models.core.results.TimeResultsFormatted import TimeResultsFormatted
from models.db.results.SimSingleResultsORM import SimSingleResultsORM
from services import MathHelper


class SimDataTransformer():
  def get_single_sims_summed(self, single_sim_results: List[SimSingleResults]) -> SimSingleResults:
    single_sims_summed = SimSingleResults.model_validate({})
    won = 0
    lost = 0
    unfinished = 0
    for r in single_sim_results:
      if r.won:
        won += 1
      elif r.won == False:
        lost += 1
      elif r.won == None:
        unfinished += 1
      single_sims_summed.hands.counts.total += int(r.hands.counts.total)
      single_sims_summed.hands.counts.blackjack += int(r.hands.counts.blackjack)
      single_sims_summed.hands.counts.won += int(r.hands.counts.won)
      single_sims_summed.hands.counts.drawn += int(r.hands.counts.drawn)
      single_sims_summed.hands.counts.lost += int(r.hands.counts.lost)
      single_sims_summed.hands.counts.surrendered += int(r.hands.counts.surrendered)
      single_sims_summed.bankroll.starting += float(r.bankroll.starting)
      single_sims_summed.bankroll.ending += float(r.bankroll.ending)
      single_sims_summed.bankroll.highest += float(r.bankroll.highest)
      single_sims_summed.bankroll.lowest += float(r.bankroll.lowest)
      single_sims_summed.bankroll.profit.total += float(r.bankroll.profit.total)
      for i in range(7):
        single_sims_summed.bankroll.profit.from_true[i] += float(r.bankroll.profit.from_true[i])
      single_sims_summed.bankroll.profit.per_hand += float(r.bankroll.profit.per_hand)
      single_sims_summed.bankroll.profit.per_hour += float(r.bankroll.profit.per_hour)
      single_sims_summed.time.human_time += float(r.time.human_time)
      single_sims_summed.time.simulation_time += float(r.time.simulation_time)
    single_sims_summed.hands.percentages = self.__get_hand_results_percentages(single_sims_summed.hands.counts)
    if won > lost:
      single_sims_summed.won = True
    elif lost < won:
      single_sims_summed.won = False
    else:
      single_sims_summed.won = None
    return single_sims_summed

  def get_single_sims_averaged(
    self,
    single_sims_summed: SimSingleResults,
    total_runs: int
  ) -> SimSingleResults:
    average_counts = HandResultsCounts.model_construct(
      total = single_sims_summed.hands.counts.total / total_runs,
      blackjack = single_sims_summed.hands.counts.blackjack / total_runs,
      won = single_sims_summed.hands.counts.won / total_runs,
      drawn = single_sims_summed.hands.counts.drawn / total_runs,
      lost = single_sims_summed.hands.counts.lost / total_runs,
      surrendered = single_sims_summed.hands.counts.surrendered / total_runs
    )
    average_percentages = HandResultsPercentages.model_construct(
      blackjack = single_sims_summed.hands.percentages.blackjack,
      won = single_sims_summed.hands.percentages.won,
      drawn = single_sims_summed.hands.percentages.drawn,
      lost = single_sims_summed.hands.percentages.lost,
      surrendered = single_sims_summed.hands.percentages.surrendered
    )
    average_hands = HandResults.model_construct(
      counts = average_counts,
      percentages = average_percentages
    )
    average_profit = ProfitResults.model_construct(
      total = single_sims_summed.bankroll.profit.total / total_runs,
      from_true = [
        single_sims_summed.bankroll.profit.from_true[0] / total_runs,
        single_sims_summed.bankroll.profit.from_true[1] / total_runs,
        single_sims_summed.bankroll.profit.from_true[2] / total_runs,
        single_sims_summed.bankroll.profit.from_true[3] / total_runs,
        single_sims_summed.bankroll.profit.from_true[4] / total_runs,
        single_sims_summed.bankroll.profit.from_true[5] / total_runs,
        single_sims_summed.bankroll.profit.from_true[6] / total_runs
      ],
      per_hand = single_sims_summed.bankroll.profit.per_hand / total_runs,
      per_hour = single_sims_summed.bankroll.profit.per_hour / total_runs
    )
    average_bankroll = BankrollResults.model_construct(
      starting = single_sims_summed.bankroll.starting / total_runs,
      ending = single_sims_summed.bankroll.ending / total_runs,
      highest = single_sims_summed.bankroll.highest / total_runs,
      lowest = single_sims_summed.bankroll.lowest / total_runs,
      profit = average_profit
    )
    average_time = TimeResults.model_construct(
      human_time = single_sims_summed.time.human_time / total_runs,
      simulation_time = single_sims_summed.time.simulation_time / total_runs
    )
    single_sims_averaged = SimSingleResults.model_construct(
      won = single_sims_summed.won,
      hands = average_hands,
      bankroll = average_bankroll,
      time = average_time
    )
    return single_sims_averaged

  def format_single_sim_results(
    self,
    results: SimSingleResults,
    hours_per_day: int,
    days_per_week: int
  ) -> SimSingleResultsFormatted:
    counts = HandResultsCountsFormatted.model_construct(
      total=f"{int(results.hands.counts.total):,}",
      blackjack=f"{int(results.hands.counts.blackjack):,}",
      won=f"{int(results.hands.counts.won):,}",
      drawn=f"{int(results.hands.counts.drawn):,}",
      lost=f"{int(results.hands.counts.lost):,}",
      surrendered=f"{int(results.hands.counts.surrendered):,}"
    )
    percentages = HandResultsPercentagesFormatted.model_construct(
      blackjack=f"{round(results.hands.percentages.blackjack, 2):.2f}%",
      won=f"{round(results.hands.percentages.won, 2):.2f}%",
      drawn=f"{round(results.hands.percentages.drawn, 2):.2f}%",
      lost=f"{round(results.hands.percentages.lost, 2):.2f}%",
      surrendered=f"{round(results.hands.percentages.surrendered, 2):.2f}%"
    )
    profit = ProfitResultsFormatted.model_construct(
      total=self.__get_formatted_bankroll(results.bankroll.profit.total),
      from_true=[
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[0]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[1]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[2]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[3]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[4]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[5]),
        self.__get_formatted_bankroll(results.bankroll.profit.from_true[6])
      ],
      per_hand=self.__get_formatted_bankroll(results.bankroll.profit.per_hand),
      per_hour=self.__get_formatted_bankroll(results.bankroll.profit.per_hour)
    )
    r_hands = HandResultsFormatted.model_construct(
      counts=counts,
      percentages=percentages
    )
    r_bankroll = BankrollResultsFormatted.model_construct(
      starting=self.__get_formatted_bankroll(results.bankroll.starting),
      ending=self.__get_formatted_bankroll(results.bankroll.ending),
      highest=self.__get_formatted_bankroll(results.bankroll.highest),
      lowest=self.__get_formatted_bankroll(results.bankroll.lowest),
      profit=profit
    )
    r_time = TimeResultsFormatted.model_construct(
      human_time=self.__get_formatted_time(results.time.human_time, hours_per_day, days_per_week),
      simulation_time=self.__get_formatted_time(results.time.simulation_time, 24, 7)
    )
    return SimSingleResultsFormatted.model_construct(
      won=results.won,
      hands=r_hands,
      bankroll=r_bankroll,
      time=r_time
    )

  def get_multi_sim_results(self, single_sim_results: List[SimSingleResults]) -> SimMultiResults | None:
    sims_run = len(single_sim_results)
    sims_won = 0
    sims_lost = 0
    sims_unfinished = 0
    simulation_time = 0.0
    human_time = 0.0
    total_hands = 0
    for result in single_sim_results:
      if result.won:
        sims_won += 1
      elif result.won is False:
        sims_lost += 1
      elif result.won is None:
        sims_unfinished += 1
      total_hands += result.hands.counts.total
      simulation_time += result.time.simulation_time
      human_time += result.time.human_time
    sims_finished = sims_run - sims_unfinished
    if sims_finished <= 0:
      return None
    success_rate = MathHelper.get_percentage(sims_won, sims_finished)
    failure_rate = MathHelper.get_percentage(sims_lost, sims_finished)
    metadata = SimMultiResultsMetadata.model_construct(
      sims_run=sims_run,
      sims_won=sims_won,
      sims_lost=sims_lost,
      sims_unfinished=sims_unfinished,
      success_rate=success_rate,
      failure_rate=failure_rate,
      total_hands=total_hands,
      simulation_time=simulation_time,
      human_time=human_time
    )

    single_sims_summed = self.get_single_sims_summed(single_sim_results)
    single_sims_averaged = self.get_single_sims_averaged(single_sims_summed, sims_run)

    multi_sim_result = SimMultiResults.model_construct(
      metadata=metadata,
      average=single_sims_averaged
    )
    return multi_sim_result

  def format_multi_sim_results(
    self,
    multi_sim_results: SimMultiResults,
    hours_per_day: int,
    days_per_week: int
  ) -> SimMultiResultsFormatted:
    sim_time = self.__get_formatted_time(
      multi_sim_results.metadata.simulation_time,
      24,
      7
    )
    human_time = self.__get_formatted_time(
      multi_sim_results.metadata.human_time,
      hours_per_day,
      days_per_week
    )
    formatted_metadata = SimMultiResultsMetadataFormatted.model_construct(
      sims_run = f"{multi_sim_results.metadata.sims_run:,}",
      sims_won = f"{multi_sim_results.metadata.sims_won:,}",
      sims_lost = f"{multi_sim_results.metadata.sims_lost:,}",
      sims_unfinished = f"{multi_sim_results.metadata.sims_unfinished:,}",
      success_rate = f"{round(multi_sim_results.metadata.success_rate, 2):.2f}%",
      failure_rate = f"{round(multi_sim_results.metadata.failure_rate, 2):.2f}%",
      total_hands = f"{multi_sim_results.metadata.total_hands:,}",
      simulation_time = f"{sim_time}",
      human_time = f"{human_time}"
    )
    formatted_single_sim_average = self.format_single_sim_results(
      multi_sim_results.average,
      hours_per_day,
      days_per_week
    )
    multi_sim_info_formatted = SimMultiResultsFormatted.model_construct(
      metadata=formatted_metadata,
      average=formatted_single_sim_average
    )
    return multi_sim_info_formatted


  def get_single_sim_req(self, multi_sim_req: CreateMultiSimReq) -> CreateSingleSimReq:
    return multi_sim_req.single

  def orm_to_pydantic(self, sim_orm: SimSingleResultsORM) -> SimSingleResults:
    return SimSingleResults(
      won=bool(sim_orm.won) if sim_orm.won is not None else None,
      hands=HandResults(
        counts=HandResultsCounts.model_validate(sim_orm.hands.counts, from_attributes=True),
        percentages=HandResultsPercentages.model_validate(sim_orm.hands.percentages, from_attributes=True)
      ),
      bankroll=BankrollResults.model_validate(sim_orm.bankroll, from_attributes=True),
      time=TimeResults.model_validate(sim_orm.time, from_attributes=True)
    )

  def __get_hand_results_percentages(self, counts: HandResultsCounts) -> HandResultsPercentages:
    percentages = HandResultsPercentages.model_construct(
      blackjack = MathHelper.get_percentage(counts.blackjack, counts.total),
      won = MathHelper.get_percentage(counts.won, counts.total),
      drawn = MathHelper.get_percentage(counts.drawn, counts.total),
      lost = MathHelper.get_percentage(counts.lost, counts.total),
      surrendered = MathHelper.get_percentage(counts.surrendered, counts.total)
    )
    return percentages

  def __get_formatted_bankroll(self, bankroll: float) -> str:
    return f"-${abs(bankroll):,.2f}" if bankroll < 0 else f"${bankroll:,.2f}"

  def __get_formatted_time(self, seconds: float, hours_per_day: int, days_per_week: int) -> str:
    if seconds > 60:
      minutes = seconds / 60
      if minutes > 60:
        hours = minutes / 60
        if hours > hours_per_day:
          days = hours / hours_per_day
          if days > days_per_week:
            weeks = days / days_per_week
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
