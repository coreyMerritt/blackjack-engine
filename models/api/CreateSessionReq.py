from pydantic import BaseModel

from models.api.PlayerInfo import PlayerInfo

class CreateSessionReq(BaseModel):
  deck_count: int
  ai_player_count: int
  min_bet: int
  max_bet: int
  player_info: PlayerInfo
  shoe_reset_percentage: int
