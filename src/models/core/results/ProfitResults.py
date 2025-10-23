from typing import List

from pydantic import BaseModel, Field


class ProfitResults(BaseModel):
  total: float = 0.0
  from_true: List[float] = Field(default_factory=lambda: [0.0] * 7)
  per_hand: float = 0.0
  per_hour: float = 0.0
