from typing import List

from pydantic import BaseModel
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules

class RunSimulationReq(BaseModel):
  money_goal: int
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
