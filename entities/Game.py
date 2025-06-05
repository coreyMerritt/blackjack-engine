import asyncio
from typing import List
from uuid import UUID
from entities.Card import Card
from entities.Dealer import Dealer
from entities.Hand import Hand
from entities.Player import Player
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from models.enums.Face import Face
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
    ai_player_info: List[AiPlayerInfo] | None
  ):
    self.__rules_engine = RulesEngine(rules)
    self.__state = GameState.NOT_STARTED
    self.__dealer = Dealer(rules.dealer_rules)

    self.__human_players = []
    self.__ai_players = []
    if ai_player_info is not None:
      for single_ai_player_info in ai_player_info:
        ai_player = AiPlayer(single_ai_player_info, self.__rules_engine)
        self.__ai_players.append(ai_player)

  async def monitor_human_states(self) -> None:
    while self.get_state() != GameState.NOT_STARTED:
      if len(self.__human_players) > 0:
        await asyncio.sleep(0.2)
        if self.get_state() == GameState.BETTING:
          players_still_betting = False
          for player in self.get_human_players():
            if player.get_hand_count() == 0:
              players_still_betting = True
          if not players_still_betting:
            self.to_next_human_state()
        else:
          if not self.is_unhandled_human_player_hand():
            self.to_next_human_state()

  def is_unhandled_human_player_hand(self) -> bool:
    active_hand = self.__calculate_active_hand()
    if active_hand is None:
      return False
    for human_player in self.__human_players:
      for hand in human_player.get_hands():
        if active_hand == hand:
          return True
    return False

  def someone_has_bankroll(self) -> bool:
    for player in self.__ai_players + self.__human_players:
      if player.get_bankroll() > 0:
        return True
    return False

  def get_dealer(self) -> Dealer:
    return self.__dealer

  def get_state(self) -> GameState:
    return self.__state

  def get_human_players(self) -> List[HumanPlayer]:
    return self.__human_players

  def get_ai_players(self) -> List[AiPlayer]:
    return self.__ai_players

  def get_human_and_ai_players(self) -> List[Player]:
    return self.__human_players + self.__ai_players

  def register_human_player(self, human_player_info: HumanPlayerInfo) -> UUID:
    self.__human_players.append(HumanPlayer(human_player_info))
    player_id = self.__human_players[-1].get_id()
    return player_id

  def start_game(self) -> None:
    if len(self.__human_players) > 0:
      asyncio.create_task(self.monitor_human_states())
    self.__to_next_state()

  def place_human_player_bet(self, player_id: str, bet: float) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        player.add_new_hand(Hand([], bet, False))
        player.decrement_bankroll(bet)
        return
    raise ValueError("player_id given does not match any existing player")

  def set_human_player_wants_insurance(self, player_id: str, insurance: bool) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        player.set_wants_insurance(insurance)
        return
    raise ValueError("player_id given does not match any existing player")

  def set_human_player_wants_surrender(self, player_id: str, surrender: bool) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        player.set_wants_surrender(surrender)
        return
    raise ValueError("player_id given does not match any existing player")

  def hit_human_player(self, player_id: str) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        for hand in player.get_hands():
          if hand == self.__calculate_active_hand():
            self.__hit_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def stand_human_player(self, player_id: str) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        for hand in player.get_hands():
          if hand == self.__calculate_active_hand():
            self.__stand_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def double_down_human_player(self, player_id: str) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        for hand in player.get_hands():
          if hand == self.__calculate_active_hand():
            self.__double_down_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def split_human_player(self, player_id: str) -> None:
    for player in self.__human_players:
      if str(player.get_id()) == str(player_id):
        for hand in player.get_hands():
          if hand == self.__calculate_active_hand():
            self.__split_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def continue_until_state(self, state: GameState) -> None:
    while True:
      if self.get_state() == state:
        return
      self.__to_next_state()

  def to_next_human_state(self) -> None:
    if self.get_state() == GameState.NOT_STARTED:
      self.continue_until_state(GameState.BETTING)
    elif self.get_state() == GameState.BETTING:
      self.continue_until_state(GameState.INSURANCE)
    elif self.get_state() == GameState.INSURANCE:
      for player in self.__ai_players + self.__human_players:
        if self.__rules_engine.can_early_surrender(player.get_hand(0)):
          self.continue_until_state(GameState.EARLY_SURRENDER)
          return
      next_state = self.__dealer_blackjack_check()
      if next_state == GameState.RESULTS:
        self.continue_until_state(GameState.BETTING)
      else:
        self.continue_until_state(next_state)

    elif self.get_state() == GameState.EARLY_SURRENDER:
      next_state = self.__dealer_blackjack_check()
      self.continue_until_state(next_state)
    elif self.get_state() == GameState.LATE_SURRENDER:
      self.continue_until_state(GameState.HUMAN_PLAYER_DECISIONS)
    elif self.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      self.continue_until_state(GameState.BETTING)
    elif self.get_state() == GameState.PAYOUTS:
      self.continue_until_state(GameState.BETTING)

  def finish_round(self) -> None:
    while self.get_state() != GameState.BETTING:
      self.__to_next_state()

  def set_state(self, state: GameState) -> None:
    BlackjackLogger.debug(f"State: {state}")
    self.__state = state

  def to_dict(self) -> dict:
    return {
      "dealer": self.__dealer.to_dict(),
      "ai_players": [p.to_dict() for p in self.__ai_players],
      "human_players": [p.to_dict() for p in self.__human_players],
      "state": self.__state.name,
    }

  def __is_unhandled_active_player_hand(self) -> bool:
    hand = self.__calculate_active_hand()
    if hand is None:
      return False
    return True

  def __is_any_competing_hand(self) -> bool:
    for player in self.__ai_players + self.__human_players:
      for hand in player.get_hands():
        hand_value = hand.get_value()
        hand_is_blackjack = hand_value == 21 and hand.get_card_count() == 2
        hand_busted = hand_value > 21
        if not hand_busted:
          if not hand_is_blackjack:
            return True
    return False

  def __calculate_active_player(self, dealer_allowed=False) -> Player | None:
    if dealer_allowed:
      if not self.__is_unhandled_active_player_hand():
        return self.__dealer
    for player in self.__human_players + self.__ai_players:
      if player.has_active_hand():
        return player
    return None

  def __calculate_active_hand(self, dealer_hand_allowed=False) -> Hand | None:
    if dealer_hand_allowed:
      if not self.__is_unhandled_active_player_hand():
        return self.__dealer.get_hand(0)
    active_player = self.__calculate_active_player()
    if active_player is None:
      return None
    return active_player.calculate_active_hand()

  def __calculate_hand_result(self, player_hand: Hand) -> HandResult:
    dealer_has_blackjack = self.__dealer.has_blackjack()
    dealer_busted = self.__dealer.calculate_if_busted()
    dealer_hand_value = self.__dealer.get_hand_value(0)

    player_hand_value = player_hand.get_value()
    player_beat_dealer = player_hand_value > dealer_hand_value
    player_has_blackjack = player_hand_value == 21 and player_hand.get_card_count() == 2

    player_busted = player_hand_value > 21
    player_tied_with_dealer = player_hand_value == dealer_hand_value
    both_have_blackjack = player_has_blackjack and dealer_has_blackjack
    only_player_has_blackjack = player_has_blackjack and not dealer_has_blackjack
    player_won = dealer_busted or player_beat_dealer
    player_lost = not dealer_busted and not player_beat_dealer

    bet = player_hand.get_bet()

    player_hand.set_finalized()
    if player_busted:
      BlackjackLogger.debug("\t\tPlayer busted!")
      return HandResult.LOSS
    elif both_have_blackjack:
      BlackjackLogger.debug("\t\tDealer & Player both have Blackjack!")
      player_hand.set_payout(0)
      return HandResult.DRAW
    elif only_player_has_blackjack:
      player_hand.set_payout(bet * self.__dealer.get_blackjack_pays_multiplier())
      return HandResult.BLACKJACK
    elif player_tied_with_dealer:
      player_hand.set_payout(0)
      return HandResult.DRAW
    elif player_won:
      player_hand.set_payout(bet)
      return HandResult.WIN
    elif player_lost:
      player_hand.set_payout(0)
      return HandResult.LOSS
    else:
      raise NotImplementedError("Unexpected conditions @dealer.handle_payout")

  def __handle_potential_21(self, hand: Hand) -> None:
    if hand.get_value() == 21:
      hand.set_finalized()

  def __handle_potential_bust(self, hand: Hand) -> None:
    hand_value = hand.get_value()
    if hand_value > 21:
      if hand.is_soft():
        hand.reset_an_ace()
        assert hand.get_value() < 21
      else:
        hand.set_finalized()
        hand.set_result(HandResult.LOSS)
        hand.set_payout(0)
        BlackjackLogger.debug("\t\tBUST!")

  def __update_running_counts(self, card: Card) -> None:
    for ai_player in self.__ai_players:
      ai_player.update_running_count(card.get_value())

###############################
# State-Related Private Methods
###############################

  def __to_next_state(self) -> None:
    if self.get_state() == GameState.NOT_STARTED:
      # Nothing needs to happen
      self.set_state(GameState.BETTING)
    elif self.get_state() == GameState.BETTING:
      self.__handle_ai_bets()
      self.set_state(GameState.DEALING)
    elif self.get_state() == GameState.DEALING:
      self.__deal_cards()
      self.set_state(GameState.PLAYER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.PLAYER_BLACKJACK_CHECK:
      self.__player_blackjack_check()
      self.set_state(GameState.INSURANCE)
    elif self.get_state() == GameState.INSURANCE:
      self.__handle_insurance()
      for player in self.__ai_players + self.__human_players:
        if self.__rules_engine.can_early_surrender(player.get_hand(0)):
          self.set_state(GameState.EARLY_SURRENDER)
          return
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)

    elif self.get_state() == GameState.EARLY_SURRENDER:
      self.__handle_early_surrender()
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.DEALER_BLACKJACK_CHECK:
      next_state = self.__dealer_blackjack_check()
      self.set_state(next_state)
    elif self.get_state() == GameState.LATE_SURRENDER:
      self.__handle_late_surrender()
      self.set_state(GameState.HUMAN_PLAYER_DECISIONS)
    elif self.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      # Human decisions should be handled via API only
      self.set_state(GameState.AI_PLAYER_DECISIONS)
    elif self.get_state() == GameState.AI_PLAYER_DECISIONS:
      self.__handle_ai_decisions()
      self.set_state(GameState.DEALER_DECISIONS)
    elif self.get_state() == GameState.DEALER_DECISIONS:
      self.__handle_dealer_decisions()
      self.set_state(GameState.RESULTS)
    elif self.get_state() == GameState.RESULTS:
      self.__set_results()
      self.set_state(GameState.PAYOUTS)
    elif self.get_state() == GameState.PAYOUTS:
      self.__handle_payouts()
      self.set_state(GameState.CLEANUP)
    elif self.get_state() == GameState.CLEANUP:
      self.__cleanup()
      self.set_state(GameState.BETTING)

  def __deal_cards(self) -> int:
    if self.__rules_engine.shoe_must_be_shuffled(self.__dealer.get_shoe()):
      BlackjackLogger.debug("\tShuffling shoe...")
      self.__dealer.load_shoe()
      self.__dealer.shuffle_shoe()
      for ai_player in self.__ai_players:
        ai_player.reset_running_count()
    self.__deal_to_players()
    self.__deal_to_dealer()

  def __deal_to_players(self) -> None:
    for player in self.__human_players + self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
      for _ in range(2):
        card = self.__dealer.draw()
        player.add_to_active_hand(card)
        BlackjackLogger.debug(f"\t\tDealt: {card.get_value()}")
        self.__update_running_counts(card)
      player_hand_value = player.calculate_active_hand().get_value()
      BlackjackLogger.debug(f"\t\tHand: {player_hand_value}")
      if player_hand_value == 21:
        BlackjackLogger.debug("\t\tBlackjack!")

  def __deal_to_dealer(self) -> None:
    self.__dealer.set_hands([Hand([], 0, False)])
    dealer_hand = self.__dealer.get_hand(0)
    BlackjackLogger.debug("\tDealer")
    for _ in range(2):
      card = self.__dealer.draw()
      dealer_hand.add_card(card)
      BlackjackLogger.debug(f"\t\tDealt: {card.get_value()}")
      self.__update_running_counts(card)
    dealer_hand_value = dealer_hand.get_value()
    BlackjackLogger.debug(f"\t\tHand: {dealer_hand_value}")
    if dealer_hand_value == 21:
      BlackjackLogger.debug("\t\tBlackjack!")

  def __handle_ai_bets(self) -> None:
    # Note: human players should set their bets before this via the API
    # if this is triggered before then, their bets will remain the same
    for player in self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
      BlackjackLogger.debug(f"\t\tDecks Remaining: {self.__dealer.get_decks_remaining()}")
      BlackjackLogger.debug(f"\t\tCards Remaining: {self.__dealer.get_decks_remaining()}")
      bet = player.calculate_bet(self.__rules_engine, self.__dealer.get_decks_remaining())
      player.add_new_hand(Hand([], bet, False))
      player.decrement_bankroll(bet)

  def __player_blackjack_check(self) -> None:
    for player in self.__human_players + self.__ai_players:
      if player.has_blackjack():
        active_hand = self.__calculate_active_hand()
        bet = active_hand.get_bet()
        if not self.__dealer.has_blackjack():
          BlackjackLogger.debug(f"\t\tPlayer-{player.get_id()}")
          BlackjackLogger.debug("\t\tBlackjack! Win!")
          active_hand.set_finalized()
          active_hand.set_result(HandResult.BLACKJACK)
          active_hand.set_payout(bet * self.__dealer.get_blackjack_pays_multiplier())
        else:
          BlackjackLogger.debug(f"\t\tDealer & Player-{player.get_id()} have Blackjack!")
          BlackjackLogger.debug("\t\tDraw!")
          active_hand.set_finalized()
          active_hand.set_result(HandResult.DRAW)
          active_hand.set_payout(0)

  def __handle_insurance(self) -> None:
    for player in self.__ai_players:
      hands = player.get_hands()
      for hand in hands:
        if self.__rules_engine.can_insure(hands, self.__dealer.get_facecard().get_face()):
          if player.wants_insurance(self.__dealer.get_facecard().get_face()):
            hand.set_insurance_bet(player.get_insurance_bet())
            player.decrement_bankroll(hand.get_insurance_bet())

  def __handle_early_surrender(self) -> None:
    for player in self.__ai_players:
      hand = player.get_hand(0)
      if player.get_hand_count() > 1:
        return False
      if self.__rules_engine.can_early_surrender(hand):
        if player.wants_to_surrender(self.__dealer.get_facecard().get_value(), self.__dealer.get_decks_remaining()):
          hand.is_finalized()
          hand.set_result(HandResult.SURRENDERED)
          hand.set_payout(hand.get_bet() / 2)

  def __dealer_blackjack_check(self) -> GameState:
    if self.__dealer.has_blackjack():
      self.__handle_insurance_payouts()
      return GameState.RESULTS
    else:
      return GameState.LATE_SURRENDER

  def __handle_insurance_payouts(self) -> None:
    for player in self.__human_players + self.__ai_players:
      for hand in player.get_hands():
        if hand.is_insured():
          if self.__dealer.has_blackjack():
            hand.is_finalized()
            hand.set_result(HandResult.LOSS)
            # The player never gets their insurance bet back naturally,
            # so payout here also covers refunding the original bet.
            hand.set_payout(hand.get_insurance_bet() * 3)

  def __handle_late_surrender(self) -> None:
    for player in self.__ai_players:
      hand = player.get_hand(0)
      if player.get_hand_count() != 1:
        return
      if self.__rules_engine.can_late_surrender(hand):
        if player.wants_to_surrender(self.__dealer.get_facecard().get_value(), self.__dealer.get_decks_remaining()):
          hand.set_payout(hand.get_bet() / 2)

  def __handle_ai_decisions(self) -> None:
    while self.__is_unhandled_active_player_hand():
      active_player = self.__calculate_active_player()
      BlackjackLogger.debug(f"\tPlayer-{active_player.get_id()}")
      if not active_player:
        break
      assert isinstance(active_player, AiPlayer), (
        "System is most likely trying to run AI decisions against a human player."
      )
      active_hand = self.__calculate_active_hand()
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
          self.__execute_decision(decision)
          break

  def __execute_decision(self, decision: PlayerDecision) -> None:
    assert self.__is_unhandled_active_player_hand()
    match decision:
      case PlayerDecision.HIT:
        self.__hit_active_hand()
      case PlayerDecision.STAND:
        self.__stand_active_hand()
      case PlayerDecision.DOUBLE_DOWN:
        self.__double_down_active_hand()
      case PlayerDecision.SPLIT:
        self.__split_active_hand()
      case PlayerDecision.SURRENDER:
        self.__surrender_active_hand()

  def __hit_active_hand(self, dealer_allowed=False) -> None:
    if not dealer_allowed:
      assert self.__is_unhandled_active_player_hand()
    active_hand = self.__calculate_active_hand(dealer_allowed)
    card = self.__dealer.draw()
    active_hand.add_card(card)
    BlackjackLogger.debug(f"\t\tHit: {card.get_value()}")
    self.__update_running_counts(card)
    BlackjackLogger.debug(f"\t\tCurrent Value: {active_hand.get_value()}")
    self.__handle_potential_bust(active_hand)
    self.__handle_potential_21(active_hand)

  def __stand_active_hand(self, silent=False, dealer_allowed=False) -> None:
    active_hand = self.__calculate_active_hand(dealer_allowed)
    if not silent:
      BlackjackLogger.debug("\t\tStand")
      BlackjackLogger.debug(f"\t\tFinal Value: {active_hand.get_value()}")
    active_hand.set_finalized()

  def __double_down_active_hand(self) -> None:
    assert self.__is_unhandled_active_player_hand()
    active_player = self.__calculate_active_player()
    active_hand = active_player.calculate_active_hand()
    active_player.decrement_bankroll(active_hand.get_bet())
    active_hand.set_finalized()
    active_hand.double_down()
    card = self.__dealer.draw()
    active_hand.add_card(card)
    BlackjackLogger.debug(f"\t\tDouble Down: {card.get_value()}")
    self.__update_running_counts(card)
    BlackjackLogger.debug(f"\t\tFinal Value: {active_hand.get_value()}")
    self.__handle_potential_bust(active_hand)
    self.__handle_potential_21(active_hand)

  def __split_active_hand(self) -> None:
    BlackjackLogger.debug("\t\tSplit")
    active_player = self.__calculate_active_player()
    active_hand = self.__calculate_active_hand()
    for card in active_hand.get_cards():
      if card.get_face() == Face.ACE:
        card.set_value(11)
    bet = active_hand.get_bet()
    active_player.decrement_bankroll(bet)
    card = active_hand.pop_card()
    new_hand = Hand([card], bet, True)
    active_player.add_new_hand(new_hand)
    for i, hand in enumerate(active_player.get_hands()):
      if hand.get_card_count() == 1:
        card = self.__dealer.draw()
        hand.add_card(card)
        BlackjackLogger.debug(f"\tHand {i}: {hand.get_card_value(0)}, {hand.get_card_value(1)} -- {hand.get_value()}")
        self.__update_running_counts(card)

  def __surrender_active_hand(self) -> None:
    active_hand = self.__calculate_active_hand()
    active_player = self.__calculate_active_player()
    BlackjackLogger.debug("\t\tSurrender")
    active_player.decrement_bankroll(active_hand.get_bet() / 2)
    active_player.get_hands().remove(active_hand)

  def __handle_dealer_decisions(self) -> None:
    assert not self.__is_unhandled_active_player_hand()
    if self.__is_any_competing_hand():
      dealer_hand = self.__dealer.get_hand(0)
      assert dealer_hand.get_card_count() == 2
      decision = PlayerDecision.PENDING
      while decision != PlayerDecision.STAND:
        if dealer_hand.get_value() > 21:
          if not dealer_hand.is_soft():
            dealer_hand.set_finalized()
            decision = PlayerDecision.STAND
            break
        decision = self.__dealer.get_decision()
        match decision:
          case PlayerDecision.HIT:
            self.__hit_active_hand(True)
      if decision == PlayerDecision.STAND:
        self.__stand_active_hand(False, True)
      return

  def __set_results(self) -> None:
    for player in self.__human_players + self.__ai_players:
      for player_hand in player.get_hands():
        BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
        player_hand_value = player_hand.get_value()
        BlackjackLogger.debug(f"\t\t{player_hand_value}")
        if player_hand.get_result() == HandResult.UNDETERMINED:
          result = self.__calculate_hand_result(player_hand)
          player_hand.set_result(result)
    dealer_hand_value = self.__dealer.get_hand(0).get_value()
    BlackjackLogger.debug("\tDealer")
    BlackjackLogger.debug(f"\t\t{dealer_hand_value}")
    if dealer_hand_value > 21:
      BlackjackLogger.debug("\t\tDealer busted!")

  def __handle_payouts(self) -> None:
    for player in self.__human_players + self.__ai_players:
      for player_hand in player.get_hands():
        result = player_hand.get_result()
        bet = player_hand.get_bet()
        payout = player_hand.get_payout()
        if result == HandResult.LOSS:
          BlackjackLogger.debug("\t\tLost!")
          self.__dealer.increment_bankroll(bet, True)
          player.increment_bankroll(payout)
        elif result == HandResult.DRAW:
          BlackjackLogger.debug("\t\tDraw!")
          player.increment_bankroll(bet, True)
          player.increment_bankroll(payout)
        elif result == HandResult.WIN:
          BlackjackLogger.debug("\t\tWin!")
          player.increment_bankroll(bet)
          player.increment_bankroll(payout)
        elif result == HandResult.BLACKJACK:
          BlackjackLogger.debug("\t\tBlackjack! Win!")
          player.increment_bankroll(bet)
          player.increment_bankroll(payout)
        elif result == HandResult.SURRENDERED:
          BlackjackLogger.debug("\t\tSurrendered!")
          self.__dealer.increment_bankroll(bet, True)
          player.increment_bankroll(payout)
        else:
          raise NotImplementedError("HandResult not implemented")

  def __cleanup(self) -> None:
    self.__reset_insurance_decisions()
    self.__reset_hands()

  def __reset_insurance_decisions(self) -> None:
    for player in self.__human_players:
      player.set_wants_insurance(False)

  def __reset_hands(self) -> None:
    for player in self.__human_players + self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
      player.set_hands([])
      BlackjackLogger.debug("\t\tReset hand to: []")

    BlackjackLogger.debug("\tDealer")
    self.__dealer.set_hands([])
    BlackjackLogger.debug("\t\tReset hand to: []\n\n")
