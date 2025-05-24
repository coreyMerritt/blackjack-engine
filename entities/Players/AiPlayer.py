import random
from entities.Player import Player
from models.enums.PlayerDecisions import PlayerDecisions


class AiPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None) -> None:
    if bet is not None:
      self.current_bet = bet
      return

    random_bet = random.randint(min_possible, max_possible)
    self.current_bet = random_bet

  def get_decision(self) -> PlayerDecisions:
    if self.get_hand_value() >= 17:
      return PlayerDecisions.STAND

    return PlayerDecisions.HIT
