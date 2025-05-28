from pydantic import BaseModel


class BettingRules(BaseModel):
  min_bet: int
  max_bet: int
