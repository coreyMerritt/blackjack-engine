from pydantic import BaseModel

from models.core.DoubleDownRestrictions import DoubleDownRestrictions


class GameRules(BaseModel):
  min_bet: int
  max_bet: int
  deck_count: int
  shoe_reset_percentage: int
  double_down_restrictions: DoubleDownRestrictions
