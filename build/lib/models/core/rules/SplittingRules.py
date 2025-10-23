from pydantic import BaseModel


class SplittingRules(BaseModel):
  maximum_hand_count: int
  can_hit_aces: bool
