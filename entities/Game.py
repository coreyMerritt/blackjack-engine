from typing import List
from entities.Dealer import Dealer
from entities.Hand import Hand
from entities.Player import Player
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from models.enums.GameState import GameState
from models.enums.HandResult import HandResult
from models.enums.PlayerDecision import PlayerDecision
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
        ai_player = AiPlayer(single_ai_player_info, self.__rules_engine)
        self.__ai_players.append(ai_player)

  def get_state(self) -> GameState:
    return self.__state

  def get_dealer(self) -> Dealer:
    return self.__dealer

  def get_human_players(self) -> List[HumanPlayer]:
    return self.__human_players

  def get_ai_players(self) -> List[AiPlayer]:
    return self.__ai_players

  def get_first_human_player_hand_value(self) -> int:
    return self.__human_players[0].get_hands()

  def get_active_hand(self) -> Hand | None:
    active_player = self.get_active_player()
    if active_player is None:
      return None
    return active_player.get_active_hand()

  def get_active_player(self) -> Player | None:
    for player in self.get_all_players_except_dealer():
      if player.has_active_hand():
        return player
    return None

  def get_all_players_except_dealer(self) -> List[Player]:
    return self.__human_players + self.__ai_players

  def set_state(self, state: GameState) -> None:
    BlackjackLogger.debug(f"State: {state}")
    self.__state = state

  def handle_ai_bets(self) -> None:
    # Note: human players should set their bets before this via the API
    # if this is triggered before then, their bets will remain the same
    for player in self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
      BlackjackLogger.debug(f"\t\tDecks Remaining: {self.__dealer.get_decks_remaining()}")
      BlackjackLogger.debug(f"\t\tCards Remaining: {self.__dealer.get_decks_remaining()}")
      bet = player.determine_bet(self.__rules_engine, self.__dealer.get_decks_remaining())
      player.set_bet(bet, 0)

  def deal_cards(self) -> int:
    if self.__rules_engine.shoe_must_be_shuffled(self.__dealer.get_shoe()):
      BlackjackLogger.debug("\tShuffling shoe...")
      self.__dealer.load_shoe()
      self.__dealer.shuffle_shoe()
      for ai_player in self.__ai_players:
        ai_player.reset_running_count()
    self.__dealer.deal(self.__human_players + self.__ai_players)

  def player_blackjack_check(self) -> None:
    for player in self.__human_players + self.__ai_players:
      if player.has_blackjack():
        if not self.__dealer.has_blackjack():
          BlackjackLogger.debug(f"\t\tPlayer-{player.get_id()}")
          BlackjackLogger.debug("\t\tBlackjack! Win!")
          active_hand = self.get_active_hand()
          active_hand.set_result(HandResult.BLACKJACK)
          active_hand.set_finalized()
        else:
          BlackjackLogger.debug(f"\t\tDealer & Player-{player.get_id()} have Blackjack!")
          BlackjackLogger.debug("\t\tDraw!")
          active_hand = self.get_active_hand()
          active_hand.set_result(HandResult.DREW)
          active_hand.set_finalized()

  def hit_active_hand(self) -> None:
    assert self.is_unhandled_active_player_hand()
    active_player = self.get_active_player()
    self.__dealer.hit_player(self.__ai_players, active_player)
    active_hand = active_player.get_active_hand()
    active_hand_value = active_hand.get_value()
    if active_hand_value > 21:
      if active_hand.is_soft():
        active_hand.reset_an_ace()
        assert active_hand.get_value() < 21
      else:
        active_hand.set_finalized()
        active_hand.set_result(HandResult.LOST)
        BlackjackLogger.debug("\t\tBUST!")
    elif active_hand_value == 21:
      active_player.finalize_active_hand()

  def stand_active_hand(self, silent=False) -> None:
    active_player = self.get_active_player()
    if not silent:
      BlackjackLogger.debug("\t\tStand")
      BlackjackLogger.debug(f"\t\tFinal Value: {self.get_active_hand().get_value()}")
    active_player.finalize_active_hand()

  def double_down_active_hand(self) -> None:
    active_player = self.get_active_player()
    self.__dealer.double_down_player(self.__ai_players, active_player)

  def split_active_hand(self) -> None:
    active_hand = self.get_active_hand()
    active_player = self.get_active_player()
    BlackjackLogger.debug("\t\tSplit")
    card = active_hand.remove_card()
    bet = active_hand.get_bet()
    new_hand = Hand([card], bet, True)
    active_player.decrement_bankroll(bet)
    active_player.add_new_hand(new_hand)
    self.__dealer.deal_split_hands(self.get_all_players_except_dealer())

  def surrender_active_hand(self) -> None:
    active_hand = self.get_active_hand()
    active_player = self.get_active_player()
    BlackjackLogger.debug("\t\tSurrender")
    active_player.decrement_bankroll(active_hand.get_bet() / 2)
    active_player.get_hands().remove(active_hand)

  def handle_dealer_decisions(self) -> None:
    for player in self.__ai_players + self.__human_players:
      for hand in player.get_hands():
        hand_value = hand.get_value()
        hand_is_blackjack = hand_value == 21 and hand.get_card_count() == 2
        hand_busted = hand_value > 21
        if not hand_busted:
          if not hand_is_blackjack:
            self.__dealer.handle_decisions(self.__ai_players)
            return

  def handle_ai_decisions(self) -> None:
    while self.is_unhandled_active_player_hand():
      active_player = self.get_active_player()
      BlackjackLogger.debug(f"\tPlayer-{active_player.get_id()}")
      if not active_player:
        break
      assert isinstance(active_player, AiPlayer), (
        "System is most likely trying to run AI decisions against a human player."
      )
      active_hand = self.get_active_hand()
      assert isinstance(active_hand, Hand)
      hand_index = active_player.get_hand_index(active_hand)
      BlackjackLogger.debug(f"\tHand-{hand_index}")
      decisions = active_player.get_decisions(
        active_hand,
        self.__dealer.get_facecard().get_value(),
        self.__dealer.get_decks_remaining()
      )
      for decision in decisions:
        if self.__rules_engine.is_legal_play(
          decision,
          active_player,
          self.get_state()
        ):
          self.execute_decision(decision)
          break

  def execute_decision(self, decision: PlayerDecision) -> None:
    assert self.is_unhandled_active_player_hand()
    match decision:
      case PlayerDecision.HIT:
        self.hit_active_hand()
      case PlayerDecision.STAND:
        self.stand_active_hand()
      case PlayerDecision.DOUBLE_DOWN:
        self.double_down_active_hand()
      case PlayerDecision.SPLIT:
        self.split_active_hand()
      case PlayerDecision.SURRENDER:
        self.surrender_active_hand()

  def handle_insurance(self) -> None:
    for player in self.__ai_players:
      hands = player.get_hands()
      for hand in hands:
        if self.__rules_engine.can_insure(hands, self.__dealer.get_facecard().get_face()):
          if player.wants_insurance(self.__dealer.get_facecard().get_face()):
            hand.set_insurance_bet(player.get_insurance_bet())

  def handle_early_surrender(self) -> None:
    for player in self.__ai_players:
      hands = player.get_hands()
      if player.get_hand_count() > 1:
        return False
      if self.__rules_engine.can_early_surrender(hands[0]):
        if player.wants_to_surrender(self.__dealer.get_facecard().get_value(), self.__dealer.get_decks_remaining()):
          player.increment_bankroll(hands[0].get_bet() / 2)
          player.set_hands([])

  def dealer_blackjack_check(self) -> GameState:
    if self.__dealer.has_blackjack():
      return GameState.PAYOUTS
    else:
      return GameState.LATE_SURRENDER

  def handle_late_surrender(self) -> None:
    for player in self.__ai_players:
      hands = player.get_hands()
      if player.get_hand_count() != 1:
        return
      if self.__rules_engine.can_late_surrender(hands[0]):
        if player.wants_to_surrender(self.__dealer.get_facecard().get_value(), self.__dealer.get_decks_remaining()):
          player.increment_bankroll(hands[0].get_bet() / 2)
          player.set_hands([])

  def continue_until_state(self, state: GameState) -> None:
    while True:
      if state == self.get_state():
        return
      self.next_state()

  def next_state(self) -> None:
    if self.get_state() == GameState.NOT_STARTED:
      # Nothing needs to happen
      self.set_state(GameState.BETTING)
    elif self.get_state() == GameState.BETTING:
      self.handle_ai_bets()
      self.set_state(GameState.DEALING)
    elif self.get_state() == GameState.DEALING:
      self.deal_cards()
      self.set_state(GameState.PLAYER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.PLAYER_BLACKJACK_CHECK:
      self.player_blackjack_check()
      self.set_state(GameState.INSURANCE)
    elif self.get_state() == GameState.INSURANCE:
      self.handle_insurance()
      self.set_state(GameState.EARLY_SURRENDER)
    elif self.get_state() == GameState.EARLY_SURRENDER:
      self.handle_early_surrender()
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.DEALER_BLACKJACK_CHECK:
      next_state = self.dealer_blackjack_check()
      self.set_state(next_state)
    elif self.get_state() == GameState.LATE_SURRENDER:
      self.handle_late_surrender()
      self.set_state(GameState.HUMAN_PLAYER_DECISIONS)
    elif self.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      # Human decisions should be handled via API only
      self.set_state(GameState.AI_PLAYER_DECISIONS)
    elif self.get_state() == GameState.AI_PLAYER_DECISIONS:
      self.handle_ai_decisions()
      self.set_state(GameState.DEALER_DECISIONS)
    elif self.get_state() == GameState.DEALER_DECISIONS:
      self.handle_dealer_decisions()
      self.set_state(GameState.PAYOUTS)
    elif self.get_state() == GameState.PAYOUTS:
      self.__dealer.handle_payouts(self.__human_players + self.__ai_players)
      self.set_state(GameState.CLEANUP)
    elif self.get_state() == GameState.CLEANUP:
      self.__dealer.reset_hands(self.__human_players + self.__ai_players)
      self.set_state(GameState.BETTING)

  def finish_round(self) -> None:
    while self.get_state() != GameState.BETTING:
      self.next_state()

  def is_unhandled_active_player_hand(self) -> bool:
    hand = self.get_active_hand()
    if hand is None:
      return False
    return True

  def someone_has_bankroll(self) -> bool:
    for player in self.__ai_players + self.__human_players:
      if player.get_bankroll() > 0:
        return True
    return False

  def to_dict(self) -> dict:
    return {
      "state": self.__state.name,
      "dealer": self.__dealer.to_dict(),
      "human_players": [p.to_dict() for p in self.__human_players],
      "ai_players": [p.to_dict() for p in self.__ai_players]
    }
