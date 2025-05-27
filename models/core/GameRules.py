from pydantic import BaseModel

from models.core.BettingRules import BettingRules
from models.core.DealerRules import DealerRules
from models.core.DoubleDownRules import DoubleDownRules
from models.core.SplittingRules import SplittingRules


class GameRules(BaseModel):
  betting_rules: BettingRules
  dealer_rules: DealerRules
  double_down_rules: DoubleDownRules
  splitting_rules: SplittingRules
