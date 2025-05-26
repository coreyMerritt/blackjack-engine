from pydantic import BaseModel

from models.core.DoubleDownRules import DoubleDownRules


class GameRules(BaseModel):
  min_bet: int
  max_bet: int
  deck_count: int
  shoe_reset_percentage: int
  double_down_rules: DoubleDownRules
