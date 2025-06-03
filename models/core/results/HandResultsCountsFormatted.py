from pydantic import BaseModel


class HandResultsCountsFormatted(BaseModel):
  total: str = ""
  won: str = ""
  lost: str = ""
  drawn: str = ""
