from typing import Optional

from pydantic import BaseModel, Field

from models.core.results.BankrollResults import BankrollResults
from models.core.results.HandResults import HandResults
from models.core.results.TimeResults import TimeResults


class SimSingleResults(BaseModel):
  won: Optional[bool] = None
  hands: HandResults = Field(default_factory=HandResults)
  bankroll: BankrollResults = Field(default_factory=BankrollResults)
  time: TimeResults = Field(default_factory=TimeResults)
