from pydantic import BaseModel


class DealerRules(BaseModel):
  dealer_hits_soft_seventeen: bool
  deck_count: int
  shoe_reset_percentage: int
  blackjack_pays_multiplier: float   # Usually: 3/2
