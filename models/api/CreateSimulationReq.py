from typing import List

from pydantic import BaseModel
from models.core.HumanTime import HumanTime
from models.core.SimulationBounds import SimulationBounds
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules

class CreateSimulationReq(BaseModel):
  bounds: SimulationBounds
  time: HumanTime
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
