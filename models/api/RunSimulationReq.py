from pydantic import BaseModel

from models.api.BetSpread import BetSpread
from models.api.PlayerInfo import PlayerInfo

class RunSimulationReq(BaseModel):
  deck_count: int
  ai_player_count: int
  min_bet: int
  max_bet: int
  shoe_reset_percentage: int
  win_value: int
  player_info: PlayerInfo
  bet_spread: BetSpread
