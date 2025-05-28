from typing import List

from entities.Hand import Hand
from entities.Player import Player
from entities.Shoe import Shoe
from entities.Card import Card, Face, Suit
from models.core.PlayerInfo import PlayerInfo
from models.core.rules.DealerRules import DealerRules
from models.enums.PlayerDecision import PlayerDecision
from services.BlackjackLogger import BlackjackLogger


class Dealer(Player):
  __hits_soft_seventeen: bool
  __blackjack_pays_multiplier: float
  __shoe: Shoe

  def __init__(self, rules: DealerRules) -> None:
    super().__init__(PlayerInfo(money=999999999))
    self.__hits_soft_seventeen = rules.dealer_hits_soft_seventeen
    self.__blackjack_pays_multiplier = rules.blackjack_pays_multiplier
    self.__shoe = Shoe(rules.deck_count, rules.shoe_reset_percentage)
    self.load_shoe()
    self.shuffle_shoe()

  def get_shoe(self) -> Shoe:
    return self.__shoe

  def get_full_shoe_size(self) -> int:
    return self.__shoe.get_full_size()

  def get_shoe_card_count(self) -> int:
    return self.__shoe.get_card_count()

  def get_shoe_reset_percentage(self) -> int:
    return self.__shoe.get_reset_percentage()

  def get_facecard(self) -> Card:
    return self.get_hands()[0].get_card(1)

  def get_money(self) -> int:
    return self.__money

  def get_active_hand_decision(self) -> PlayerDecision:
    if self.get_hands()[0].is_soft():
      if self.get_hand_value(0) == 17:
        if self.__hits_soft_seventeen:
          return PlayerDecision.HIT
        return PlayerDecision.STAND
    if self.get_hand_value(0) >= 17:
      return PlayerDecision.STAND
    else:
      return PlayerDecision.HIT

  def deal(self, players: List[Player]) -> None:
    for player in players:
      for _ in range(2):
        card = self.__shoe.draw()
        player.add_to_active_hand(card)
        BlackjackLogger.debug(f"Dealt Player-{player.get_id()}: {card.get_value()}")

    self.set_hands([Hand([], 0, False)])
    dealer_hand = self.get_hands()[0]
    for _ in range(2):
      card = self.__shoe.draw()
      dealer_hand.add_card(card)
      BlackjackLogger.debug(f"Dealt dealer: {card.get_value()}")

  def shuffle_shoe(self) -> None:
    BlackjackLogger.debug("Shuffling shoe...")
    self.__shoe.shuffle()

  def load_shoe(self) -> None:
    BlackjackLogger.debug("Loading shoe...")
    shoe_deck_count = self.__shoe.get_deck_count()
    shoe_full_size = self.__shoe.get_full_size()
    self.__shoe.set_cards([])

    for _ in range(shoe_deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.__shoe.add_card(card)
    assert self.__shoe.get_card_count() == shoe_full_size

  def hit_player(self, player: Player) -> None:
    assert isinstance(player, Player)
    card = self.__shoe.draw()
    player.add_to_active_hand(card)

  def stand_player(self, player: Player) -> None:
    player.finalize_active_hand()

  def handle_decisions(self) -> None:
    if self.get_hand_count() == 0:
      return
    decision = PlayerDecision.PLACEHOLDER
    while decision != PlayerDecision.STAND:
      decision = self.get_active_hand_decision()
      match decision:
        case PlayerDecision.HIT:
          self.hit_player(self)

  def handle_payouts(self, players: List[Player]) -> None:
    dealer_hand_value = self.get_hand_value(0)
    dealer_busted = dealer_hand_value > 21
    dealer_has_blackjack = dealer_hand_value == 21 and self.get_hands()[0].get_card_count() == 2
    BlackjackLogger.debug("End of hand:")
    BlackjackLogger.debug(f"\tDealer has: {dealer_hand_value}")
    if dealer_busted:
      BlackjackLogger.debug("\t\tDealer busted!")
    for player in players:
      for player_hand_index, player_hand in enumerate(player.get_hands()):
        self.handle_single_standard_payout(
          player,
          player_hand,
          player_hand_index,
          dealer_hand_value,
          dealer_has_blackjack,
          dealer_busted
        )
        self.handle_single_insurance_payout(player, player_hand, dealer_has_blackjack)

  def handle_single_standard_payout(self,
    player: Player,
    player_hand: Hand,
    hand_index: int,
    dealer_hand_value: int,
    dealer_has_blackjack: bool,
    dealer_busted: bool
  ) -> None:
    player_hand_value = player.get_hand_value(hand_index)
    player_beat_dealer = player_hand_value > dealer_hand_value
    player_has_blackjack = player_hand_value == 21 and player_hand.get_card_count() == 2

    player_busted = player_hand_value > 21
    player_tied_with_dealer = player_hand_value == dealer_hand_value
    both_have_blackjack = player_has_blackjack and dealer_has_blackjack
    only_player_has_blackjack = player_has_blackjack and not dealer_has_blackjack
    player_won = dealer_busted or player_beat_dealer
    player_lost = not dealer_busted and not player_beat_dealer

    BlackjackLogger.debug(f"\tPlayer-{player.get_id()} has: {player_hand_value}")
    if player_busted:
      BlackjackLogger.debug("\t\tPlayer busted!")
      self.increment_money(player_hand.get_bet())
    elif both_have_blackjack:
      BlackjackLogger.debug("\t\tBoth players have Blackjack! Draw!")
      player.increment_money(player_hand.get_bet())
    elif player_tied_with_dealer:
      BlackjackLogger.debug("\t\tDraw!")
      player.increment_money(player_hand.get_bet())
    elif only_player_has_blackjack:
      BlackjackLogger.debug("\t\tPlayer has Blackjack! Win!")
      player.increment_money(player_hand.get_bet() + (player_hand.get_bet() * self.__blackjack_pays_multiplier))
    elif player_won:
      BlackjackLogger.debug("\t\tPlayer won!")
      player.increment_money(player_hand.get_bet() * 2)
    elif player_lost:
      BlackjackLogger.debug("\t\tPlayer lost!")
      self.increment_money(player_hand.get_bet())
    else:
      raise NotImplementedError("Unexpected conditions @dealer.handle_payout")
    player.set_bet(0, hand_index)

  def handle_single_insurance_payout(self,
    player: Player,
    player_hand: Hand,
    dealer_has_blackjack: bool
  ) -> None:
    if player_hand.is_insured():
      if dealer_has_blackjack:
        player.increment_money(player_hand.get_insurance_bet() * 2)
      player_hand.set_insurance_bet(0)

  def reset_hands(self, players: List[Player]) -> None:
    for i, player in enumerate(players):
      player.set_hands([])
      BlackjackLogger.debug(f"Reset player-{i} hand to: []")
    self.set_hands([])
    BlackjackLogger.debug("Reset dealer hand to: []\n\n")   

  def to_dict(self) -> dict:
    return {
      "shoe": self.__shoe.to_dict(),
      "hand": [c.to_dict() for hand in self.get_hands() for c in hand.get_cards()]
    }
