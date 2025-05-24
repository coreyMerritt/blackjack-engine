from typing import List
from pydantic import BaseModel

from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo

class CreateSessionReq(BaseModel):
  rules: GameRules
  human_player_info: HumanPlayerInfo
  ai_player_info: List[AiPlayerInfo]
