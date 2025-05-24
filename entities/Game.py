from typing import List
from entities.Dealer import Dealer
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.DoubleDownRestrictions import DoubleDownRestrictions
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo
from models.enums.GameState import GameState
from services.BasicStrategyEngine import BasicStrategyEngine


class Game:
  min_bet: int
  max_bet: int
  state: GameState
  dealer: Dealer
  human_players: List[HumanPlayer]
  ai_players: List[AiPlayer]
  double_down_restrictions: DoubleDownRestrictions
  basic_strategy_engine: BasicStrategyEngine

  def __init__(
    self,
    rules: GameRules,
    human_player_info: List[HumanPlayerInfo] | None,
    ai_player_info: List[AiPlayerInfo] | None
  ) -> None:
    self.human_players = []
    if human_player_info is not None:
      for single_human_player_info in human_player_info:
        human_player = HumanPlayer(single_human_player_info)   # TODO: AI players should get their own info
        self.human_players.append(human_player)

    self.ai_players = []
    if ai_player_info is not None:
      for single_ai_player_info in ai_player_info:
        ai_player = AiPlayer(single_ai_player_info)   # TODO: AI players should get their own info
        self.ai_players.append(ai_player)

    self.dealer = Dealer(rules.deck_count, rules.shoe_reset_percentage)
    self.dealer.load_shoe()
    self.dealer.shuffle_shoe()

    self.rules = rules
    self.basic_strategy_engine = BasicStrategyEngine()
    self.state = GameState.NOT_STARTED

  def to_dict(self) -> dict:
    return {
      "max_bet": self.max_bet,
      "min_bet": self.min_bet,
      "state": self.state.name,
      "dealer": self.dealer.to_dict(),
      "human_players": [p.to_dict() for p in self.human_players],
      "ai_players": [p.to_dict() for p in self.ai_players]
    }
