from pydantic import BaseModel, Field

from models.core.results.ProfitResultsFormatted import ProfitResultsFormatted


class BankrollResultsFormatted(BaseModel):
  starting: str = ""
  ending: str = ""
  highest: str = ""
  lowest: str = ""
  profit: ProfitResultsFormatted = Field(default_factory=ProfitResultsFormatted)
