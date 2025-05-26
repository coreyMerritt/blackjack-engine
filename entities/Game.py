from typing import List
from entities.Dealer import Dealer
from entities.Hand import Hand
from entities.Player import Player
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.DoubleDownRules import DoubleDownRules
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo
from models.enums.GameState import GameState
from services.BasicStrategyEngine import BasicStrategyEngine
from services.BlackjackLogger import BlackjackLogger


class Game:
  _min_bet: int
  _max_bet: int
  _state: GameState
  _dealer: Dealer
  _human_players: List[HumanPlayer]
  _ai_players: List[AiPlayer]
  _double_down_rules: DoubleDownRules
  _basic_strategy_engine: BasicStrategyEngine

  def __init__(
    self,
    rules: GameRules,
    human_player_info: List[HumanPlayerInfo] | None,
    ai_player_info: List[AiPlayerInfo] | None
  ) -> None:
    self._human_players = []
    if human_player_info is not None:
      for single_human_player_info in human_player_info:
        human_player = HumanPlayer(single_human_player_info)   # TODO: AI players should get their own info
        self._human_players.append(human_player)

    self._ai_players = []
    if ai_player_info is not None:
      for single_ai_player_info in ai_player_info:
        ai_player = AiPlayer(single_ai_player_info)   # TODO: AI players should get their own info
        self._ai_players.append(ai_player)

    self._dealer = Dealer(rules.deck_count, rules.shoe_reset_percentage)
    self._dealer.load_shoe()
    self._dealer.shuffle_shoe()

    self._rules = rules
    self._basic_strategy_engine = BasicStrategyEngine()
    self._state = GameState.NOT_STARTED

  def get_first_human_player_hand_value(self) -> int:
    return self._human_players[0].get_hands()

  def get_state(self) -> GameState:
    return self._state

  # TODO: We need to completely rework how state is handled, maybe remove SimulationEngine?
  def set_state(self, state: GameState) -> None:
    self._state = state

  def place_bets(self, bet: int) -> None:
    all_players_except_dealer = self._human_players + self._ai_players
    for player in all_players_except_dealer:
      player.place_bet(bet, self._rules)

  def deal_cards(self) -> int:
    self.set_state(GameState.DEALING)
    full_shoe = self._dealer.get_full_shoe_size()
    shoe_card_count = self._dealer.get_shoe_card_count()
    stopping_point = full_shoe / (100 / self._dealer.get_shoe_reset_percentage())
    shoe_is_above_reset_point = shoe_card_count > stopping_point
    BlackjackLogger.debug(f"shoe_card_count: {shoe_card_count}")
    BlackjackLogger.debug(f"stopping_point: {stopping_point}")
    if not shoe_is_above_reset_point:
      BlackjackLogger.debug("Shuffling shoe...")
      self._dealer.load_shoe()
      self._dealer.shuffle_shoe()
    else:
      BlackjackLogger.debug("Shoe does not need to be shuffled")
    all_players = self._human_players + self._ai_players
    self._dealer.deal(all_players)

  def hit_active_hand(self) -> None:
    active_player = self._get_active_player()
    self._dealer.hit_player(active_player)

  def _get_active_hand(self) -> Hand:
    active_player = self._get_active_player()
    return active_player.get_active_hand()

  def _get_active_player(self) -> Player:
    for player in self._get_all_players_except_dealer():
      active_hand = player.get_active_hand()
      if active_hand is not None:
        return player

  def _get_all_players_except_dealer(self) -> List[Player]:
    return self._human_players + self._ai_players

  def to_dict(self) -> dict:
    return {
      "max_bet": self._max_bet,
      "min_bet": self._min_bet,
      "state": self._state.name,
      "dealer": self._dealer.to_dict(),
      "human_players": [p.to_dict() for p in self._human_players],
      "ai_players": [p.to_dict() for p in self._ai_players]
    }
