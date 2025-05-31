from pydantic import BaseModel, Field
from models.core.results.ProfitFromTrue import ProfitFromTrue


class BankrollResults(BaseModel):
  starting: float = 0
  ending: float = 0
  total_profit: float = 0
  profit_from_true: ProfitFromTrue = Field(default_factory=ProfitFromTrue)
  profit_per_hand: float = 0
  profit_per_hour: float = 0
  peak: float = 0
