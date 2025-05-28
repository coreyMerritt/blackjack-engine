from pydantic import BaseModel


class HandResults(BaseModel):
  count: int
  percent: str

class MoneyResults(BaseModel):
  starting: str
  ending: str
  total_profit: str
  profit_per_hand: str
  profit_per_hour: str
  peak: str

class TimeResults(BaseModel):
  human_time: str
  simulation_time: str

class SimulationResultsFormattedRes(BaseModel):
  total_hands_played: str
  hands_won: HandResults
  hands_lost: HandResults
  hands_drawn: HandResults
  money: MoneyResults
  time: TimeResults
