from pydantic import BaseModel

from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo


class RegisterHumanPlayerReq(BaseModel):
  human_player_info: HumanPlayerInfo
