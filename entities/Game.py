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
from services.RulesEngine import RulesEngine


class Game:
  __rules_engine: RulesEngine
  __state: GameState
  __dealer: Dealer
  __human_players: List[HumanPlayer]
  __ai_players: List[AiPlayer]

  def __init__(
    self,
    rules: GameRules,
    human_player_info: List[HumanPlayerInfo] | None,
    ai_player_info: List[AiPlayerInfo] | None
  ) -> None:
    self.__rules_engine = RulesEngine(rules)
    self.__state = GameState.NOT_STARTED
    self.__dealer = Dealer(rules.dealer_rules)

    self.__human_players = []
    if human_player_info is not None:
      for single_human_player_info in human_player_info:
        human_player = HumanPlayer(single_human_player_info)
        self.__human_players.append(human_player)

    self.__ai_players = []
    if ai_player_info is not None:
      for single_ai_player_info in ai_player_info:
        ai_player = AiPlayer(single_ai_player_info)
        self.__ai_players.append(ai_player)
    self.__double_down_rules = rules.double_down_rules
    self.__basic_strategy_engine = BasicStrategyEngine()

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

  def get_active_hand(self) -> Hand | None:
    active_player = self.get_active_player()
    return active_player.get_active_hand()

  def get_active_player(self) -> Player | None:
    for player in self.get_all_players_except_dealer():
      if player.has_active_hand():
        return player
    return None

  def get_all_players_except_dealer(self) -> List[Player]:
    return self.__human_players + self.__ai_players

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

  def place_bets(self) -> None:
    # Note: human players should set their bets before this via the API
    # if this is triggered before then, their bets will remain the same
    for player in self.__ai_players:
      bet = player.determine_bet()
      player.set_bet(bet)

  def deal_cards(self) -> int:
    self.set_state(GameState.DEALING)
    if self.__rules_engine.shoe_must_be_shuffled(self.__dealer.get_shoe()):
      BlackjackLogger.debug("Shuffling shoe...")
      self.__dealer.load_shoe()
      self.__dealer.shuffle_shoe()
    else:
      BlackjackLogger.debug("Shoe does not need to be shuffled")
    self.__dealer.deal(self.__human_players + self.__ai_players)

  def hit_active_hand(self) -> None:
    active_player = self.get_active_player()
    self.__dealer.hit_player(active_player)

  def stand_active_hand(self) -> None:
    active_player = self.get_active_player()
    active_player.finalize_active_hand()

  def double_down_active_hand(self) -> None:
    assert self.active_hand_can_double_down()
    active_hand = self.get_active_hand()
    active_hand.double_down()
    self.hit_active_hand()
    if active_hand.get_value() < 21:
      self.stand_active_hand()

  def handle_ai_decisions(self) -> None:
    for ai_player in self.__ai_players:
      for hand_index, hand in enumerate(ai_player.get_hands()):
        player_decision = [PlayerDecision.PLACEHOLDER]
        while True:
          for decision in player_decision:
            match decision:
              case PlayerDecision.PLACEHOLDER:
                pass
              case PlayerDecision.HIT:
                self.hit_active_hand()
              case PlayerDecision.STAND:
                break
              case PlayerDecision.DOUBLE_DOWN:
                if self.active_hand_can_double_down():
                  self.double_down_active_hand()
                  break
              case PlayerDecision.SPLIT:
                card = hand.remove_card()
                new_hand = Hand([card], hand.get_bet(), True)
                ai_player.add_new_hand(new_hand)
              case PlayerDecision.SURRENDER:
                if self.__rules_engine.can_surrender():

                break

          if ai_player.get_hand_value(hand_index) >= 21:
            break

          player_decision = BasicStrategyEngine.get_play(
            ai_player.get_basic_strategy_skill_level(),
            hand,
            self.__dealer.get_facecard(),
            True,   # TODO: Implement
            False   # TODO: Implement
          )
          BlackjackLogger.debug(f"Decision: {player_decision}")

  def handle_early_insurance(self) -> None:
    for player in self.__human_players + self.__ai_players:
      for hand in player.get_hands():
        if hand.is_insured():
          player.decrement_money(hand.get_bet() / 2)
          player.set_hands(player.get_hands().remove(hand))

  def next_state(self) -> None:
    if self.get_state() == GameState.NOT_STARTED:
      self.set_state(GameState.BETTING)
    elif self.get_state() == GameState.BETTING:
      self.place_bets()
    elif self.get_state() == GameState.INSURANCE:
      self.handle_insurance()
    elif self.get_state() == GameState.EARLY_SURRENDER:
      self.handle_early_surrender()
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.DEALER_BLACKJACK_CHECK:
      self.dealer_blackjack_check()
      self.set_state(GameState.LATE_SURRENDER)
    elif self.get_state() == GameState.LATE_SURRENDER:
      self.handle_late_surrender()
      self.set_state(GameState.HUMAN_PLAYER_DECISIONS)
    elif self.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      self.set_state(GameState.AI_PLAYER_DECISIONS)
    elif self.get_state() == GameState.AI_PLAYER_DECISIONS:
      self.handle_ai_decisions()
      self.set_state(GameState.DEALER_DECISIONS)
    elif self.get_state() == GameState.DEALER_DECISIONS:
      self.__dealer.handle_decisions()
      self.set_state(GameState.PAYOUTS)
    elif self.get_state() == GameState.PAYOUTS:
      self.__dealer.handle_payouts(self.__human_players + self.__ai_players)
      self.set_state(GameState.CLEANUP)
    elif self.get_state() == GameState.CLEANUP:
      self.__dealer.reset_hands(self.__human_players + self.__ai_players)
      self.set_state(GameState.BETTING)

  def finish_round(self) -> None:
    if self.get_state() == GameState.NOT_STARTED:
      self.set_state(GameState.BETTING)
    if self.get_state() == GameState.BETTING:
      self.place_bets()
      self.set_state(GameState.EARLY_INSURANCE)
    if self.get_state() == GameState.EARLY_INSURANCE:
      self.handle_early_insurance()
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)
    if self.get_state() == GameState.DEALER_BLACKJACK_CHECK:
      self.dealer_blackjack_check()
      self.set_state(GameState.LATE_INSURANCE)
    if self.get_state() == GameState.LATE_INSURANCE:
      self.handle_late_insurance()
      self.set_state(GameState.HUMAN_PLAYER_DECISIONS)
    if self.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      self.set_state(GameState.AI_PLAYER_DECISIONS)
    if self.get_state() == GameState.AI_PLAYER_DECISIONS:
      self.handle_ai_decisions()
      self.set_state(GameState.DEALER_DECISIONS)
    if self.get_state() == GameState.DEALER_DECISIONS:
      self.__dealer.handle_decisions()
      self.set_state(GameState.PAYOUTS)
    if self.get_state() == GameState.PAYOUTS:
      self.__dealer.handle_payouts(self.__human_players + self.__ai_players)
      self.set_state(GameState.CLEANUP)
    if self.get_state() == GameState.CLEANUP:
      self.__dealer.reset_hands(self.__human_players + self.__ai_players)
      self.set_state(GameState.BETTING)



  EARLY_INSURANCE = 3
  DEALER_BLACKJACK_CHECK = 4
  LATE_INSURANCE = 5










  def to_dict(self) -> dict:
    return {
      "state": self.__state.name,
      "dealer": self.__dealer.to_dict(),
      "human_players": [p.to_dict() for p in self.__human_players],
      "ai_players": [p.to_dict() for p in self.__ai_players]
    }
