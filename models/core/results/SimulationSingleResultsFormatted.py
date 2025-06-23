from typing import Optional
from pydantic import BaseModel, Field

from models.core.results.TimeResultsFormatted import TimeResultsFormatted
from models.core.results.HandResultsFormatted import HandResultsFormatted
from models.core.results.BankrollResultsFormatted import BankrollResultsFormatted


class SimulationSingleResultsFormatted(BaseModel):
  won: Optional[bool] = None
  hands: HandResultsFormatted = Field(default_factory=HandResultsFormatted)
  bankroll: BankrollResultsFormatted = Field(default_factory=BankrollResultsFormatted)
  time: TimeResultsFormatted = Field(default_factory=TimeResultsFormatted)
