from typing import List

from pydantic import BaseModel
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules

class CreateSimulationReq(BaseModel):
  bankroll_goal: int
  human_time_limit: int | None
  sim_time_limit: int | None
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
