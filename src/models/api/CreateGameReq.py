from typing import List

from pydantic import BaseModel

from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from models.core.rules.GameRules import GameRules


class CreateGameReq(BaseModel):
  rules: GameRules
  ai_player_info: List[AiPlayerInfo]
