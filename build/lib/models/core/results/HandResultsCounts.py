from pydantic import BaseModel


class HandResultsCounts(BaseModel):
  total: int = 0
  blackjack: int = 0
  won: int = 0
  drawn: int = 0
  lost: int = 0
  surrendered: int = 0
