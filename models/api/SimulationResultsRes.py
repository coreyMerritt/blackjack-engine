from pydantic import BaseModel

from models.core.results.HandResults import HandResults
from models.core.results.MoneyResults import MoneyResults
from models.core.results.TimeResults import TimeResults


class SimulationResultsRes(BaseModel):
  total_hands_played: int
  hands_won: HandResults
  hands_lost: HandResults
  hands_drawn: HandResults
  money: MoneyResults
  time: TimeResults
