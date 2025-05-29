from pydantic import BaseModel


class HandResultsFormatted(BaseModel):
  count: int = 0
  percent: str = ""
