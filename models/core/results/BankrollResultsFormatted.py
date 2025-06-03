from typing import List
from pydantic import BaseModel


class BankrollResultsFormatted(BaseModel):
  starting: str = ""
  ending: str = ""
  total_profit: str = ""
  profit_from_true: List[str] = ["", "", "", "", "", "", ""]
  profit_per_hand: str = ""
  profit_per_hour: str = ""
  peak: str = ""
