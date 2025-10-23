import asyncio
from typing import List

from entities.Card import Card
from entities.Dealer import Dealer
from entities.Hand import Hand
from entities.Player import Player
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from models.core.rules.GameRules import GameRules
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
        state = self.get_state()
        if state == GameState.BETTING:
          still_betting = False
          for human_player in self.__human_players:
            if human_player.get_hand_count() == 0:
              still_betting = True
              break
          if not still_betting:
            self.to_next_human_state()
        if state == GameState.INSURANCE:
          still_deciding_on_insurance = False
          for human_player in self.__human_players:
            if human_player.get_hand(0).is_insured() is None:
              still_deciding_on_insurance = True
              break
          if not still_deciding_on_insurance:
            self.to_next_human_state()
        if state == GameState.EARLY_SURRENDER or state == GameState.LATE_SURRENDER:
          still_deciding_on_surrender = False
          for human_player in self.__human_players:
            if human_player.get_hand(0).is_surrendered() is None:
              still_deciding_on_surrender = True
              break
          if not still_deciding_on_surrender:
            self.to_next_human_state()
        if state == GameState.HUMAN_PLAYER_DECISIONS:
          still_playing_hands = False
          for human_player in self.__human_players:
            if human_player.has_active_hand():
              still_playing_hands = True
              break
          if not still_playing_hands:
            self.to_next_human_state()

  def is_unhandled_human_player_hand(self) -> bool:
    state = self.get_state()
    if state != GameState.HUMAN_PLAYER_DECISIONS:
      raise RuntimeError(f"This method should not be called in State: {self.get_state()}")
    active_hand = self.__calculate_active_hand()
    if active_hand is None:
      return False
    for human_player in self.__human_players:
      for hand in human_player.get_hands():
        if active_hand == hand:
          return True
    return False

  def someone_has_bankroll(self) -> bool:
    for player in self.__human_players + self.__ai_players:
      if player.get_bankroll() > 0:
        return True
    return False

  def get_player(self, player_id: str) -> Player:
    for player in self.__human_players + self.__ai_players:
      if player.get_id() == player_id:
        return player
    raise ValueError("Given an ID that matches no existing player")

  def get_dealer(self) -> Dealer:
    return self.__dealer

  def get_state(self) -> GameState:
    return self.__state

  def calculate_active_player(self) -> Player:
    state = self.get_state()
    dealer = self.get_dealer()
    if state == GameState.BETTING:
      for player in self.__human_players + self.__ai_players:
        if player.get_hand_count() == 0:
          return player
      raise RuntimeError(f"State is {state} but no Player is active...")
    if state == GameState.INSURANCE:
      for player in self.__human_players + self.__ai_players:
        if player.get_hand(0).is_insured() is None:
          return player
      raise RuntimeError(f"State is {state} but no Player is active...")
    if state == GameState.EARLY_SURRENDER or state == GameState.LATE_SURRENDER:
      for player in self.__human_players + self.__ai_players:
        if player.get_hand(0).is_surrendered() is None:
          return player
      raise RuntimeError(f"State is {state} but no Player is active...")
    if state == GameState.HUMAN_PLAYER_DECISIONS:
      for human_player in self.__human_players:
        if human_player.has_active_hand():
          return human_player
      raise RuntimeError(f"State is {state} but no Human Player is active...")
    if state == GameState.AI_PLAYER_DECISIONS:
      for ai_player in self.__ai_players:
        if ai_player.has_active_hand():
          return ai_player
      raise RuntimeError(f"State is {state} but no AI Player is active...")
    if state == GameState.DEALER_DECISIONS:
      return dealer
    raise RuntimeError(f"This method should not be called in State: {self.get_state()}")

  def get_human_players(self) -> List[HumanPlayer]:
    return self.__human_players

  def get_ai_players(self) -> List[AiPlayer]:
    return self.__ai_players

  def get_human_and_ai_players(self) -> List[HumanPlayer | AiPlayer]:
    return self.__human_players + self.__ai_players

  def register_human_player(self, human_player_info: HumanPlayerInfo) -> str:
    self.__human_players.append(HumanPlayer(human_player_info))
    player_id = self.__human_players[-1].get_id()
    return player_id

  def reset_game(self) -> None:
    self.set_state(GameState.NOT_STARTED)
    for player in self.__human_players + self.__ai_players + [self.__dealer]:
      player.reset_bankroll()

  def start_game(self) -> None:
    if len(self.__human_players) > 0:
      asyncio.create_task(self.monitor_human_states())
    self.__to_next_state()

  def place_human_player_bet(self, player_id: str, bet: float) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        human_player.add_new_hand(Hand([], bet, False))
        human_player.decrement_bankroll(bet)
        return
    raise ValueError("player_id given does not match any existing player")

  def set_human_player_wants_insurance(self, player_id: str, insurance: bool) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        if insurance:
          self.__insure_player_hand(human_player)
          return
        human_player.get_hand(0).set_insured(False)
        return
    raise ValueError("player_id given does not match any existing player")

  def set_human_player_wants_surrender(self, player_id: str, surrender: bool) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        if surrender:
          self.__surrender_player_hand(human_player)
          return
        else:
          human_player.get_hand(0).set_surrendered(False)
          return
    raise ValueError("player_id given does not match any existing player")

  def hit_human_player(self, player_id: str) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        for hand in human_player.get_hands():
          if hand == self.__calculate_active_hand():
            assert self.calculate_active_player() == human_player
            assert self.__rules_engine.is_legal_play(PlayerDecision.HIT, human_player, self.get_state())
            self.__hit_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def stand_human_player(self, player_id: str) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        for hand in human_player.get_hands():
          if hand == self.__calculate_active_hand():
            assert self.calculate_active_player() == human_player
            assert self.__rules_engine.is_legal_play(PlayerDecision.STAND, human_player, self.get_state())
            self.__stand_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def double_down_human_player(self, player_id: str) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        for hand in human_player.get_hands():
          if hand == self.__calculate_active_hand():
            assert self.calculate_active_player() == human_player
            assert self.__rules_engine.is_legal_play(PlayerDecision.DOUBLE_DOWN, human_player, self.get_state())
            self.__double_down_active_hand()
            return
    raise ValueError("The given player_id does not match the active player")

  def split_human_player(self, player_id: str) -> None:
    for human_player in self.__human_players:
      if str(human_player.get_id()) == str(player_id):
        for hand in human_player.get_hands():
          if hand == self.__calculate_active_hand():
            assert self.calculate_active_player() == human_player
            assert self.__rules_engine.is_legal_play(PlayerDecision.SPLIT, human_player, self.get_state())
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
      for player in self.__human_players + self.__ai_players:
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
    try:
      self.__calculate_active_hand()
      return True
    except RuntimeError:
      return False

  def __is_any_competing_hand(self) -> bool:
    for player in self.__human_players + self.__ai_players:
      for hand in player.get_hands():
        hand_value = hand.get_value()
        hand_is_blackjack = hand_value == 21 and hand.get_card_count() == 2
        hand_busted = hand_value > 21
        if not hand_busted:
          if not hand_is_blackjack:
            return True
    return False

  def __calculate_active_hand(self) -> Hand:
    active_player = self.calculate_active_player()
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

  def __insure_player_hand(self, player: Player) -> None:
    hand = player.get_hand(0)
    insurance_bet = hand.get_bet() / 2
    hand.set_insured()
    hand.set_insurance_bet(insurance_bet)
    player.decrement_bankroll(insurance_bet)

  def __surrender_player_hand(self, player: Player) -> None:
    hand = player.get_hand(0)
    BlackjackLogger.debug("\t\tSurrender")
    player.increment_bankroll(hand.get_bet() / 2)
    hand.set_finalized()
    hand.set_surrendered()
    hand.set_result(HandResult.SURRENDERED)

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
      self.__handle_ai_players_insurance()
      for player in self.__human_players + self.__ai_players:
        if self.__rules_engine.can_early_surrender(player.get_hand(0)):
          self.set_state(GameState.EARLY_SURRENDER)
          return
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)

    elif self.get_state() == GameState.EARLY_SURRENDER:
      self.__handle_ai_players_early_surrender()
      self.set_state(GameState.DEALER_BLACKJACK_CHECK)
    elif self.get_state() == GameState.DEALER_BLACKJACK_CHECK:
      next_state = self.__dealer_blackjack_check()
      self.set_state(next_state)
    elif self.get_state() == GameState.LATE_SURRENDER:
      self.__handle_ai_players_late_surrender()
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

  def __deal_cards(self) -> None:
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
    for ai_player in self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{ai_player.get_id()}")
      BlackjackLogger.debug(f"\t\tDecks Remaining: {self.__dealer.get_decks_remaining()}")
      BlackjackLogger.debug(f"\t\tCards Remaining: {self.__dealer.get_decks_remaining()}")
      assert self.calculate_active_player() == ai_player
      bet = ai_player.calculate_bet(self.__rules_engine, self.__dealer.get_decks_remaining())
      ai_player.add_new_hand(Hand([], bet, False))
      ai_player.decrement_bankroll(bet)

  def __player_blackjack_check(self) -> None:
    for player in self.__human_players + self.__ai_players:
      if player.has_blackjack():
        blackjack_hand = player.get_hand(0)
        bet = blackjack_hand.get_bet()
        if not self.__dealer.has_blackjack():
          BlackjackLogger.debug(f"\t\tPlayer-{player.get_id()}")
          BlackjackLogger.debug("\t\tBlackjack! Win!")
          blackjack_hand.set_finalized()
          blackjack_hand.set_result(HandResult.BLACKJACK)
          blackjack_hand.set_payout(bet * self.__dealer.get_blackjack_pays_multiplier())
        else:
          BlackjackLogger.debug(f"\t\tDealer & Player-{player.get_id()} have Blackjack!")
          BlackjackLogger.debug("\t\tDraw!")
          blackjack_hand.set_finalized()
          blackjack_hand.set_result(HandResult.DRAW)
          blackjack_hand.set_payout(0)

  def __handle_ai_players_insurance(self) -> None:
    for ai_player in self.__ai_players:
      assert self.calculate_active_player() == ai_player
      if self.__rules_engine.can_insure(ai_player.get_hands(), self.__dealer.get_facecard().get_face()):
        if ai_player.wants_insurance(self.__dealer.get_facecard()):
          self.__insure_player_hand(ai_player)
          return
      ai_player.get_hand(0).set_insured(False)

  def __handle_ai_players_early_surrender(self) -> None:
    for ai_player in self.__ai_players:
      hand = ai_player.get_hand(0)
      if ai_player.get_hand_count() != 1:
        return
      if self.__rules_engine.can_late_surrender(hand):
        if ai_player.wants_to_surrender(self.__dealer.get_facecard(), self.__dealer.get_decks_remaining()):
          assert self.calculate_active_player() == ai_player
          self.__surrender_player_hand(ai_player)
          return
      ai_player.get_hand(0).set_surrendered(False)

  def __dealer_blackjack_check(self) -> GameState:
    if self.__dealer.has_blackjack():
      self.__handle_players_insurance_payouts()
      return GameState.RESULTS
    else:
      return GameState.LATE_SURRENDER

  def __handle_players_insurance_payouts(self) -> None:
    for player in self.__human_players + self.__ai_players:
      for hand in player.get_hands():
        if hand.is_insured():
          if self.__dealer.has_blackjack():
            hand.is_finalized()
            hand.set_result(HandResult.LOSS)
            # The player never gets their insurance bet back naturally,
            # so payout here also covers refunding the original bet.
            hand.set_payout(hand.get_insurance_bet() * 3)

  def __handle_ai_players_late_surrender(self) -> None:
    for ai_player in self.__ai_players:
      if not ai_player.get_hand(0).is_surrendered():
        hand = ai_player.get_hand(0)
        if ai_player.get_hand_count() != 1:
          return
        if self.__rules_engine.can_late_surrender(hand):
          if ai_player.wants_to_surrender(self.__dealer.get_facecard(), self.__dealer.get_decks_remaining()):
            assert self.calculate_active_player() == ai_player
            self.__surrender_player_hand(ai_player)
            return
        ai_player.get_hand(0).set_surrendered(False)

  def __handle_ai_decisions(self) -> None:
    for ai_player in self.__ai_players:
      for hand in ai_player.get_hands():
        while not hand.is_finalized():
          assert self.calculate_active_player() == ai_player
          BlackjackLogger.debug(f"\tPlayer-{ai_player.get_id()}")
          if not ai_player:
            break
          assert isinstance(ai_player, AiPlayer), (
            "System is most likely trying to run AI decisions against a human player."
          )
          active_hand = self.__calculate_active_hand()
          assert isinstance(active_hand, Hand)
          hand_index = ai_player.get_hand_index(active_hand)
          BlackjackLogger.debug(f"\tHand-{hand_index}")
          decisions = ai_player.get_decisions(
            active_hand,
            self.__dealer.get_facecard().get_value(),
            self.__dealer.get_decks_remaining()
          )
          for decision in decisions:
            if self.__rules_engine.is_legal_play(
              decision,
              ai_player,
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

  def __hit_active_hand(self) -> None:
    active_hand = self.__calculate_active_hand()
    card = self.__dealer.draw()
    active_hand.add_card(card)
    BlackjackLogger.debug(f"\t\tHit: {card.get_value()}")
    self.__update_running_counts(card)
    BlackjackLogger.debug(f"\t\tCurrent Value: {active_hand.get_value()}")
    self.__handle_potential_bust(active_hand)
    self.__handle_potential_21(active_hand)

  def __stand_active_hand(self, silent=False) -> None:
    active_hand = self.__calculate_active_hand()
    if not silent:
      BlackjackLogger.debug("\t\tStand")
      BlackjackLogger.debug(f"\t\tFinal Value: {active_hand.get_value()}")
    active_hand.set_finalized()

  def __double_down_active_hand(self) -> None:
    assert self.__is_unhandled_active_player_hand()
    active_player = self.calculate_active_player()
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
    active_player = self.calculate_active_player()
    active_hand = self.__calculate_active_hand()
    for card in active_hand.get_cards():
      if card.get_face() == Face.ACE:
        card.set_value(11)
    bet = active_hand.get_bet()
    active_player.decrement_bankroll(bet)
    active_hand.set_from_split(True)
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
    active_player = self.calculate_active_player()
    BlackjackLogger.debug("\t\tSurrender")
    active_player.increment_bankroll(active_hand.get_bet() / 2)
    active_player.get_hands().remove(active_hand)

  def __handle_dealer_decisions(self) -> None:
    dealer = self.get_dealer()
    assert self.calculate_active_player() == dealer
    if self.__is_any_competing_hand():
      dealer_hand = self.__dealer.get_hand(0)
      assert dealer_hand.get_card_count() == 2
      decision = PlayerDecision.PENDING
      while decision != PlayerDecision.STAND:
        if dealer.get_hand_value(0) >= 21:
          dealer_hand.set_finalized()
          return
        decision = self.__dealer.get_decision()
        match decision:
          case PlayerDecision.HIT:
            self.__hit_active_hand()
      if decision == PlayerDecision.STAND:
        self.__stand_active_hand()
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
          assert player_hand.is_surrendered()
          self.__dealer.increment_bankroll(bet / 2, True)
          # The half bet should already be returned before now
        else:
          raise NotImplementedError("HandResult not implemented")

  def __cleanup(self) -> None:
    self.__reset_hands()

  def __reset_hands(self) -> None:
    for player in self.__human_players + self.__ai_players:
      BlackjackLogger.debug(f"\tPlayer-{player.get_id()}")
      player.set_hands([])
      BlackjackLogger.debug("\t\tReset hand to: []")

    BlackjackLogger.debug("\tDealer")
    self.__dealer.set_hands([])
    BlackjackLogger.debug("\t\tReset hand to: []\n\n")
