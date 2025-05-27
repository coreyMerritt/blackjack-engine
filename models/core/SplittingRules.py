from pydantic import BaseModel


class SplittingRules(BaseModel):
  maximum_hand_count: int
