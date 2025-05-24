from random import shuffle
from typing import List
from entities.Player import Player
from entities.Shoe import Shoe
from entities.Players.AiPlayer import AiPlayer
from entities.Card import Card, Face, Suit
from models.enums.PlayerDecision import PlayerDecision
from services.BlackjackLogger import blackjack_logger


class Dealer:
  shoe: Shoe
  hand: List[Card]

  def __init__(self, deck_count) -> None:
    self.hand = []
    self.shoe = Shoe(deck_count)

  def deal(self, players: List[Player]) -> None:
    for player in players:
      for _ in range(2):
        player.hand.append(self.shoe.cards.pop())
    for _ in range(2):
      self.hand.append(self.shoe.cards.pop())

  def shuffle_shoe(self) -> None:
    blackjack_logger.debug("Shuffling shoe...")
    shuffle(self.shoe.cards)

  def load_shoe(self) -> None:
    blackjack_logger.debug("Loading shoe...")
    self.shoe.cards = []

    for _ in range(self.shoe.deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.cards.append(card)

    self.shoe.full_size = 52 * self.shoe.deck_count
    assert self.shoe.full_size == len(self.shoe.cards)

  def hit(self, player: Player) -> None:
    blackjack_logger.debug(f"Shoe size: {len(self.shoe.cards)}")
    blackjack_logger.debug(f"Hitting the player from: {player.get_hand_value()}")
    player.hand.append(self.shoe.cards.pop())

  def handle_ai_decisions(self, ai_players: List[AiPlayer]) -> None:
    for i, ai_player in enumerate(ai_players):
      decision = PlayerDecision.PLACEHOLDER
      while decision != PlayerDecision.STAND:
        match decision:
          case PlayerDecision.HIT:
            blackjack_logger.debug(f"Shoe size: {len(self.shoe.cards)}")
            blackjack_logger.debug(f"Hitting the AI #{i} from: {ai_player.get_hand_value()}")
            ai_player.hand.append(self.shoe.cards.pop())
        decision = ai_player.get_decision()

  def handle_dealer_decisions(self) -> None:
    decision = PlayerDecision.PLACEHOLDER
    while decision != PlayerDecision.STAND:
      decision = self.get_decision()
      match decision:
        case PlayerDecision.HIT:
          self.hand.append(self.shoe.cards.pop())

  def get_decision(self) -> PlayerDecision:
    if self.get_hand_value() >= 17:
      return PlayerDecision.STAND
    else:
      return PlayerDecision.HIT

  def get_hand_value(self) -> int:
    value = 0
    for card in self.hand:
      value += card.value

    return value

  def handle_payouts(self, players: List[Player]) -> None:
    dealer_hand_value = self.get_hand_value()
    dealer_busted = dealer_hand_value > 21
    dealer_has_blackjack = dealer_hand_value == 21 and len(self.hand) == 2
    for player in players:
      player_hand_value = player.get_hand_value()
      player_busted = player_hand_value > 21
      player_beat_dealer = player_hand_value > dealer_hand_value
      player_has_blackjack = player_hand_value == 21 and len(player.hand) == 2
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
    for player in players:
      player.hand = []
    self.hand = []

  def to_dict(self) -> dict:
    return {
      "shoe": self.shoe.to_dict(),
      "hand": [h.to_dict() for h in self.hand]
    }
