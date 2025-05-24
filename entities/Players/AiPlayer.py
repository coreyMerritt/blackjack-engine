import random
from entities.Player import Player
from models.enums.PlayerDecision import PlayerDecision


class AiPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None) -> None:
    if bet is not None:
      self.current_bet = bet
      return

    random_bet = random.randint(min_possible, max_possible)
    self.current_bet = random_bet

  def get_decision(self) -> PlayerDecision:
    if self.get_hand_value() >= 17:
      return PlayerDecision.STAND

    return PlayerDecision.HIT
