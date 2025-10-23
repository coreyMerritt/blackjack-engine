from pydantic import BaseModel


class HandResultsPercentages(BaseModel):
  blackjack: float = 0.0
  won: float = 0.0
  drawn: float = 0.0
  lost: float = 0.0
  surrendered: float = 0.0
