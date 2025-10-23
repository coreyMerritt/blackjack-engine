from pydantic import BaseModel


class HandResultsCountsFormatted(BaseModel):
  total: str = ""
  blackjack: str = ""
  won: str = ""
  drawn: str = ""
  lost: str = ""
  surrendered: str = ""
