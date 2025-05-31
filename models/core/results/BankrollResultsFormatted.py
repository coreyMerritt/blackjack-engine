from pydantic import BaseModel, Field
from models.core.results.ProfitFromTrueFormatted import ProfitFromTrueFormatted


class BankrollResultsFormatted(BaseModel):
  starting: str = ""
  ending: str = ""
  total_profit: str = ""
  profit_from_true: ProfitFromTrueFormatted = Field(default_factory=ProfitFromTrueFormatted)
  profit_per_hand: str = ""
  profit_per_hour: str = ""
  peak: str = ""
