from pydantic import BaseModel, Field

from models.core.results.TimeResultsFormatted import TimeResultsFormatted
from models.core.results.HandResultsFormatted import HandResultsFormatted
from models.core.results.BankrollResultsFormatted import BankrollResultsFormatted


class SimulationSingleResultsFormatted(BaseModel):
  total_hands_played: int = 0
  hands_won: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  hands_lost: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  hands_drawn: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  bankroll: BankrollResultsFormatted = Field(default_factory=BankrollResultsFormatted)
  time: TimeResultsFormatted = Field(default_factory=TimeResultsFormatted)
