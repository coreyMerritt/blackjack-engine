from pydantic import BaseModel


class BettingRules(BaseModel):
  min_bet: float
  max_bet: float
