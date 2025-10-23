from pydantic import BaseModel


class HandResultsPercentagesFormatted(BaseModel):
  blackjack: str = ""
  won: str = ""
  drawn: str = ""
  lost: str = ""
  surrendered: str = ""
