from pydantic import BaseModel, Field

from models.core.results.HandResults import HandResults
from models.core.results.BankrollResults import BankrollResults
from models.core.results.TimeResults import TimeResults


class SimulationSingleResults(BaseModel):
  total_hands_played: int = 0
  hands_won: HandResults = Field(default_factory=HandResults)
  hands_lost: HandResults = Field(default_factory=HandResults)
  hands_drawn: HandResults = Field(default_factory=HandResults)
  bankroll: BankrollResults = Field(default_factory=BankrollResults)
  time: TimeResults = Field(default_factory=TimeResults)
