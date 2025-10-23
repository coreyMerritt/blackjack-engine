from typing import List
from pydantic import BaseModel


class ProfitResultsFormatted(BaseModel):
  total: str = ""
  from_true: List[str] = ["", "", "", "", "", "", ""]
  per_hand: str = ""
  per_hour: str = ""
