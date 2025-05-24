from pydantic import BaseModel

from models.core.DoubleDownRestrictions import DoubleDownRestrictions
from models.core.PlayerInfo import PlayerInfo

class CreateSessionReq(BaseModel):
  deck_count: int
  ai_player_count: int
  min_bet: int
  max_bet: int
  shoe_reset_percentage: int
  double_down_restrictions: DoubleDownRestrictions
  player_info: PlayerInfo
