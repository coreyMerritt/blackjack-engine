from pydantic import BaseModel

from models.core.BettingRules import BettingRules
from models.core.DealerRules import DealerRules
from models.core.DoubleDownRules import DoubleDownRules


class GameRules(BaseModel):
  hand_split_limit: int
  dealer_rules: DealerRules
  betting_rules: BettingRules
  double_down_rules: DoubleDownRules
