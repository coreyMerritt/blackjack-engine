from typing import List
from pydantic import BaseModel, Field


class BankrollResults(BaseModel):
  starting: float = 0
  ending: float = 0
  total_profit: float = 0
  profit_from_true: List[float] = Field(default_factory=lambda: [0.0] * 7)
  profit_per_hand: float = 0
  profit_per_hour: float = 0
  peak: float = 0
