from models.core.BetSpread import BetSpread
from models.core.player_info.PlayerInfo import PlayerInfo

class AiPlayerInfo(PlayerInfo):
  counts_cards: bool
  plays_deviations: bool
  basic_strategy_skill_level: int
  card_counting_skill_level: int
  deviations_skill_level: int
  bet_spread: BetSpread
