from pydantic import BaseModel, Field

from models.core.results.HandResults import HandResults
from models.core.results.MoneyResults import MoneyResults
from models.core.results.TimeResults import TimeResults


class SimulationSingleResults(BaseModel):
  total_hands_played: int = 0
  hands_won: HandResults = Field(default_factory=HandResults)
  hands_lost: HandResults = Field(default_factory=HandResults)
  hands_drawn: HandResults = Field(default_factory=HandResults)
  bankroll: MoneyResults = Field(default_factory=MoneyResults)
  time: TimeResults = Field(default_factory=TimeResults)
