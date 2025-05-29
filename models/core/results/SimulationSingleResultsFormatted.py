from pydantic import BaseModel, Field

from models.core.results.TimeResultsFormatted import TimeResultsFormatted
from models.core.results.HandResultsFormatted import HandResultsFormatted
from models.core.results.MoneyResultsFormatted import MoneyResultsFormatted


class SimulationSingleResultsFormatted(BaseModel):
  total_hands_played: int = 0
  hands_won: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  hands_lost: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  hands_drawn: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  money: MoneyResultsFormatted = Field(default_factory=MoneyResultsFormatted)
  time: TimeResultsFormatted = Field(default_factory=TimeResultsFormatted)
