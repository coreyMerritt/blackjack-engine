from random import shuffle
from typing import List

from pydantic_core import to_json
from entities.Player import Player
from entities.Shoe import Shoe
from entities.Players.AiPlayer import AiPlayer
from entities.Card import Card, Face, Suit
from models.core.GameRules import GameRules
from models.enums.PlayerDecision import PlayerDecision
from services.BasicStrategyEngine import BasicStrategyEngine
from services.BlackjackLogger import BlackjackLogger


class Dealer:
  shoe: Shoe
  hand: List[Card]

  def __init__(self, shoe_deck_count: int, shoe_reset_percentage: int) -> None:
    self.hand = []
    self.shoe = Shoe(shoe_deck_count, shoe_reset_percentage)

  def deal(self, players: List[Player]) -> None:
    for i, player in enumerate(players):
      for _ in range(2):
        card = self.shoe.cards.pop()
        player.hand.append(card)
        BlackjackLogger.debug(f"Dealt player-{i}: {card.value}")
    for _ in range(2):
      self.hand.append(self.shoe.cards.pop())
      BlackjackLogger.debug(f"Dealt dealer: {card.value}")

  def shuffle_shoe(self) -> None:
    BlackjackLogger.debug("Shuffling shoe...")
    shuffle(self.shoe.cards)

  def load_shoe(self) -> None:
    BlackjackLogger.debug("Loading shoe...")
    self.shoe.cards = []

    for _ in range(self.shoe.deck_count):
      for suit in Suit:
        for face in Face:
          card = Card(suit, face)
          self.shoe.cards.append(card)

    self.shoe.full_size = 52 * self.shoe.deck_count
    assert self.shoe.full_size == len(self.shoe.cards)

  def hit(self, player: Player) -> None:
    BlackjackLogger.debug(f"Shoe size: {len(self.shoe.cards)}")
    BlackjackLogger.debug(f"Hitting the player from: {player.get_hand_value()}")
    player.hand.append(self.shoe.cards.pop())
    if player.get_hand_value() > 21:
      for card in player.hand:
        if card.value_can_reset:
          card.value_can_reset = False
          card.value = 1
          break

  def handle_ai_decisions(self, ai_players: List[AiPlayer], rules: GameRules) -> None:
    for i, ai_player in enumerate(ai_players):
      player_decision = PlayerDecision.PLACEHOLDER
      while True:
        match player_decision:
          case PlayerDecision.PLACEHOLDER:
            pass
          case PlayerDecision.HIT:
            BlackjackLogger.debug(f"Shoe size: {len(self.shoe.cards)}")
            BlackjackLogger.debug(f"Hitting the AI #{i} from: {ai_player.get_hand_value()}")
            ai_player.hand.append(self.shoe.cards.pop())
          case PlayerDecision.STAND:
            break
          case PlayerDecision.DOUBLE_DOWN_HIT:
            # TODO: This isn't a proper implementation -- just hits for now
            BlackjackLogger.debug(f"Shoe size: {len(self.shoe.cards)}")
            BlackjackLogger.debug(f"Hitting the AI #{i} from: {ai_player.get_hand_value()}")
            ai_player.hand.append(self.shoe.cards.pop())
          case PlayerDecision.DOUBLE_DOWN_STAND:
            # TODO: This isn't a proper implementation -- just stands for now
            break
          case PlayerDecision.SPLIT:
            # TODO: This isn't a proper implementation -- just stands for now
            break
          case PlayerDecision.SURRENDER:
            # TODO: This isn't a proper implementation -- just stands for now
            break

        player_decision = BasicStrategyEngine.get_play(
          ai_player.basic_strategy_skill_level,
          ai_player.hand,
          self.hand[1],
          True,   # TODO: Implement
          False   # TODO: Implement
        )
        BlackjackLogger.debug(f"Decision: {player_decision}")

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
    for i, player in enumerate(players):
      player.hand = []
      BlackjackLogger.debug(f"Reset player-{i} hand to: []")
    self.hand = []
    BlackjackLogger.debug(f"Reset dealer hand to: []")

  def to_dict(self) -> dict:
    return {
      "shoe": self.shoe.to_dict(),
      "hand": [h.to_dict() for h in self.hand]
    }
