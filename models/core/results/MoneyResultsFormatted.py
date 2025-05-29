from pydantic import BaseModel


class MoneyResultsFormatted(BaseModel):
  starting: str = ""
  ending: str = ""
  total_profit: str = ""
  profit_per_hand: str = ""
  profit_per_hour: str = ""
  peak: str = ""
