from typing import List

from pydantic import BaseModel
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules

class CreateSimulationReq(BaseModel):
  money_goal: int
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
