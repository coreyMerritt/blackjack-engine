from pydantic import BaseModel, Field
from models.core.results.ProfitResults import ProfitResults


class BankrollResults(BaseModel):
  starting: float = 0.0
  ending: float = 0.0
  highest: float = 0.0
  lowest: float = 0.0
  profit: ProfitResults = Field(default_factory=ProfitResults)
