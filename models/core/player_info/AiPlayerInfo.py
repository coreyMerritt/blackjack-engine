from models.core.BetSpread import BetSpread
from models.core.player_info.PlayerInfo import PlayerInfo

class AiPlayerInfo(PlayerInfo):
  basic_strategy_skill_level: int
  bet_spread: BetSpread
