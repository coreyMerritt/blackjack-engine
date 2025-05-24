from typing import List

from pydantic import BaseModel
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.BetSpread import BetSpread
from models.core.GameRules import GameRules

class RunSimulationReq(BaseModel):
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
  money_goal: int
  bet_spread: BetSpread
