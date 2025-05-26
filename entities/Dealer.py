from random import shuffle
from typing import List

from entities.Hand import Hand
from entities.Player import Player
from entities.Shoe import Shoe
from entities.Players.AiPlayer import AiPlayer
from entities.Card import Card, Face, Suit
from models.core.DoubleDownRules import DoubleDownRules
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.BlackjackEngine import BlackjackEngine
from services.BlackjackLogger import BlackjackLogger


class Dealer:
  __shoe: Shoe
  __hands: List[Hand]

  def __init__(self, shoe_deck_count: int, shoe_reset_percentage: int) -> None:
    self.__hands = []
    self.__shoe = Shoe(shoe_deck_count, shoe_reset_percentage)

  def get_full_shoe_size(self) -> int:
    return self.__shoe.get_full_size()

  def get_shoe_card_count(self) -> int:
    return self.__shoe.get_card_count()

  def get_shoe_reset_percentage(self) -> int:
    return self.__shoe.get_reset_percentage()

  def deal(self, players: List[Player]) -> None:
    for i, player in enumerate(players):
      player.hands[0] = Hand([], False, False)
      for _ in range(2):
        card = self.__shoe.cards.pop()
        player.hands[0].add_card(card)
        BlackjackLogger.debug(f"Dealt player-{i}: {card.value}")

    self.__hands[0] = Hand([], False, False)
    for _ in range(2):
      card = self.__shoe.cards.pop()
      self.__hands[0].add_card(card)
      BlackjackLogger.debug(f"Dealt dealer: {card.value}")

  def shuffle_shoe(self) -> None:
    BlackjackLogger.debug("Shuffling shoe...")
    shuffle(self.__shoe.cards)

  def load_shoe(self) -> None:
    BlackjackLogger.debug("Loading shoe...")
    shoe_deck_count = self.__shoe.get_deck_count()
    shoe_full_size = self.__shoe.get_full_size()
    self.__shoe.cards = []

    for _ in range(shoe_deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.__shoe.cards.append(card)

    assert len(self.__shoe.get_card_count()) == shoe_full_size

  def hit_player(self, player: Player) -> None:
    card = self.__shoe.draw()
    player.add_to_active_hand(card)

  def stand(self, player: Player, hand_index: int) -> None:
    # TODO: We really need to fix hands to implement this
    pass

  def handle_dealer_decisions(self) -> None:
    decision = PlayerDecision.PLACEHOLDER
    while decision != PlayerDecision.STAND:
      # TODO: This name is awful
      decision = self.get_decision()
      match decision:
        case PlayerDecision.HIT:
          # TODO: Shouldn't we use self.hit here?
          self.__hands[0].cards.append(self.__shoe.cards.pop())
          self.hit_player(self)

  def get_decision(self) -> PlayerDecision:
    if self.get_hand_value() >= 17:
      return PlayerDecision.STAND
    else:
      return PlayerDecision.HIT

  # TODO: This should be simpler now
  def get_hand_value(self) -> int:
    value = 0
    for card in self.__hands[0].cards:
      value += card.value

    return value

  def get_facecard(self) -> Card:
    return self.__hands[0].get_card(1)

  def handle_payouts(self, players: List[Player]) -> None:
    dealer_hand_value = self.get_hand_value()
    dealer_busted = dealer_hand_value > 21
    dealer_has_blackjack = dealer_hand_value == 21 and len(self.__hands[0].cards) == 2
    for player in players:
      for i, player_hand in enumerate(player.hands):
        player_hand_value = player.get_hand_value(i)
        player_busted = player_hand_value > 21
        player_beat_dealer = player_hand_value > dealer_hand_value
        player_has_blackjack = player_hand_value == 21 and len(player_hand) == 2
        player_tied_with_dealer = player_hand_value == dealer_hand_value

        both_have_blackjack = player_has_blackjack and dealer_has_blackjack
        only_player_has_blackjack = player_has_blackjack and not dealer_has_blackjack
        player_won = dealer_busted or player_beat_dealer
        player_lost = not dealer_busted and not player_beat_dealer

        if player_busted:
          player.money -= player.current_bet
        elif both_have_blackjack:
          pass  # Push/Tie
        elif only_player_has_blackjack:
          player.money += (player.current_bet * 1.5)
        elif player_won:
          player.money += player.current_bet
        elif player_tied_with_dealer:
          pass  # Push/Tie
        elif player_lost:
          player.money -= player.current_bet
        else:
          raise NotImplementedError("Unexpected conditions @dealer.handle_payout")

  def reset_hands(self, players: List[Player]) -> None:
    for i, player in enumerate(players):
      player.hands = []
      BlackjackLogger.debug(f"Reset player-{i} hand to: []")
    self.__hands = []
    BlackjackLogger.debug("Reset dealer hand to: []")

  def to_dict(self) -> dict:
    return {
      "shoe": self.__shoe.to_dict(),
      "hand": [c.to_dict() for hand in self.__hands for c in hand.cards]
    }
