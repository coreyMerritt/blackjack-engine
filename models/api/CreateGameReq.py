from typing import List
from pydantic import BaseModel

from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo

class CreateGameReq(BaseModel):
  rules: GameRules
  human_player_info: HumanPlayerInfo
  ai_player_info: List[AiPlayerInfo]
