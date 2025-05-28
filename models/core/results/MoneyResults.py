from pydantic import BaseModel


class MoneyResults(BaseModel):
  starting: float
  ending: float
  total_profit: float
  profit_per_hand: float
  profit_per_hour: float
  peak: float