from typing import List
from pydantic import BaseModel


class BankrollResults(BaseModel):
  starting: float = 0
  ending: float = 0
  total_profit: float = 0
  profit_from_true: List[float] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  profit_per_hand: float = 0
  profit_per_hour: float = 0
  peak: float = 0
