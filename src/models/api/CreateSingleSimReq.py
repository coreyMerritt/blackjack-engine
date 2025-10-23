from typing import List

from pydantic import BaseModel
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules

class CreateSingleSimReq(BaseModel):
  bounds: SingleSimBounds
  time: HumanTime
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
