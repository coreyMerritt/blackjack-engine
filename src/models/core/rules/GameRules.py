from pydantic import BaseModel

from models.core.rules.BettingRules import BettingRules
from models.core.rules.DealerRules import DealerRules
from models.core.rules.DoubleDownRules import DoubleDownRules
from models.core.rules.SplittingRules import SplittingRules
from models.core.rules.SurrenderRules import SurrenderRules


class GameRules(BaseModel):
  betting_rules: BettingRules
  dealer_rules: DealerRules
  double_down_rules: DoubleDownRules
  splitting_rules: SplittingRules
  surrender_rules: SurrenderRules
