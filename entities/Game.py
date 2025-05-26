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
from models.enums.Face import Face
from models.enums.GameState import GameState
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.BlackjackLogger import BlackjackLogger


class Game:
  __min_bet: int
  __max_bet: int
  __state: GameState
  __dealer: Dealer
  __human_players: List[HumanPlayer]
  __ai_players: List[AiPlayer]
  __double_down_rules: DoubleDownRules
  __basic_strategy_engine: BasicStrategyEngine

  def __init__(
    self,
    rules: GameRules,
    human_player_info: List[HumanPlayerInfo] | None,
    ai_player_info: List[AiPlayerInfo] | None
  ) -> None:
    self.__human_players = []
    if human_player_info is not None:
      for single_human_player_info in human_player_info:
        human_player = HumanPlayer(single_human_player_info)   # TODO: AI players should get their own info
        self.__human_players.append(human_player)

    self.__ai_players = []
    if ai_player_info is not None:
      for single_ai_player_info in ai_player_info:
        ai_player = AiPlayer(single_ai_player_info)   # TODO: AI players should get their own info
        self.__ai_players.append(ai_player)

    self.__dealer = Dealer(rules.deck_count, rules.shoe_reset_percentage)
    self.__dealer.load_shoe()
    self.__dealer.shuffle_shoe()

    self._rules = rules
    self.__basic_strategy_engine = BasicStrategyEngine()
    self.__state = GameState.NOT_STARTED

  def get_min_bet(self) -> int:
    return self.__min_bet

  def get_max_bet(self) -> int:
    return self.__max_bet

  def get_state(self) -> GameState:
    return self.__state

  def get_dealer(self) -> Dealer:
    return self.__dealer

  def get_human_players(self) -> List[HumanPlayer]:
    return self.__human_players

  def get_ai_players(self) -> List[AiPlayer]:
    return self.__ai_players

  def get_double_down_rules(self) -> DoubleDownRules:
    return self.__double_down_rules

  def get_basic_strategy_engine(self) -> BasicStrategyEngine:
    return self.__basic_strategy_engine

  def get_first_human_player_hand_value(self) -> int:
    return self.__human_players[0].get_hands()

  def get_active_hand(self) -> Hand:
    active_player = self.get_active_player()
    return active_player.get_active_hand()

  def get_active_player(self) -> Player:
    for player in self.get_all_players_except_dealer():
      active_hand = player.get_active_hand()
      if active_hand is not None:
        return player

  def get_all_players_except_dealer(self) -> List[Player]:
    return self.__human_players + self.__ai_players

  # TODO: We need to completely rework how state is handled, maybe remove SimulationEngine?
  def set_state(self, state: GameState) -> None:
    self.__state = state

  def active_hand_can_double_down(self) -> bool:
    active_hand = self.get_active_hand()
    if active_hand.is_doubled_down():
      return False
    if not active_hand.is_pair():
      return False
    if self.__double_down_rules.first_two_cards_only and active_hand.get_card_count() != 2:
      return False
    if not self.__double_down_rules.allow_after_split and active_hand.is_from_split():
      return False

    # Its important that we check this by Face because aces can change value
    both_cards_are_ace = active_hand.get_card_face(0) == Face.ACE
    both_cards_are_ten = active_hand.get_card_value(0) == 10
    both_cards_are_nine = active_hand.get_card_value(0) == 9
    if self.__double_down_rules.nine_ten_eleven_only and not (
      both_cards_are_ace
      or both_cards_are_ten
      or both_cards_are_nine
    ):
      return False

    return True

  def place_bets(self, bet: int) -> None:
    all_players_except_dealer = self.__human_players + self.__ai_players
    for player in all_players_except_dealer:
      player.place_bet(bet, self._rules)

  def deal_cards(self) -> int:
    self.set_state(GameState.DEALING)
    full_shoe = self.__dealer.get_full_shoe_size()
    shoe_card_count = self.__dealer.get_shoe_card_count()
    stopping_point = full_shoe / (100 / self.__dealer.get_shoe_reset_percentage())
    shoe_is_above_reset_point = shoe_card_count > stopping_point
    BlackjackLogger.debug(f"shoe_card_count: {shoe_card_count}")
    BlackjackLogger.debug(f"stopping_point: {stopping_point}")
    if not shoe_is_above_reset_point:
      BlackjackLogger.debug("Shuffling shoe...")
      self.__dealer.load_shoe()
      self.__dealer.shuffle_shoe()
    else:
      BlackjackLogger.debug("Shoe does not need to be shuffled")
    all_players = self.__human_players + self.__ai_players
    self.__dealer.deal(all_players)

  def hit_active_hand(self) -> None:
    active_player = self.get_active_player()
    self.__dealer.hit_player(active_player)

  def stand_active_hand(self) -> None:
    active_player = self.get_active_player()
    active_player.finalize_active_hand()

  def handle_ai_decisions(self) -> None:
    for ai_player in self.__ai_players:
      for hand_index, hand in enumerate(ai_player.hands):
        player_decision = PlayerDecision.PLACEHOLDER
        while True:
          match player_decision:
            case PlayerDecision.PLACEHOLDER:
              pass
            case PlayerDecision.HIT:
              self.__dealer.hit_player(ai_player)
            case PlayerDecision.STAND:
              break
            case PlayerDecision.DOUBLE_DOWN_HIT:
              # TODO: This isn't a proper implementation -- just hits for now
              if hand.can_double_down(self.__double_down_rules):    # Not implemented
                pass
            case PlayerDecision.DOUBLE_DOWN_STAND:
              # TODO: This isn't a proper implementation -- just stands for now
              break
            case PlayerDecision.SPLIT:
              # TODO: This isn't a proper implementation -- just stands for now
              break
            case PlayerDecision.SURRENDER:
              # TODO: This isn't a proper implementation -- just stands for now
              break

          if ai_player.get_hand_value(hand_index) >= 21:
            break

          player_decision = BasicStrategyEngine.get_play(
            ai_player.basic_strategy_skill_level,
            hand,
            self.__dealer.get_facecard(),
            True,   # TODO: Implement
            False   # TODO: Implement
          )
          BlackjackLogger.debug(f"Decision: {player_decision}")

  # TODO: We should make this more "state aware" and callable from any state
  def finish_round(self) -> None:
    self.set_state(GameState.AI_PLAYER_DECISIONS)
    self.handle_ai_decisions()
    self.set_state(GameState.DEALER_DECISIONS)
    self.__dealer.handle_dealer_decisions()
    self.set_state(GameState.PAYOUTS)
    all_players = self.__human_players + self.__ai_players
    self.__dealer.handle_payouts(all_players)
    self.set_state(GameState.CLEANUP)
    self.__dealer.reset_hands(all_players)
    self.set_state(GameState.BETTING)

  def to_dict(self) -> dict:
    return {
      "max_bet": self.__max_bet,
      "min_bet": self.__min_bet,
      "state": self.__state.name,
      "dealer": self.__dealer.to_dict(),
      "human_players": [p.to_dict() for p in self.__human_players],
      "ai_players": [p.to_dict() for p in self.__ai_players]
    }
