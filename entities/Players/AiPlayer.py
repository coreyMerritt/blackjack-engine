import random
from entities.Player import Player

class AiPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None):
    if bet is not None:
      self.current_bet = bet
      return

    random_bet = random.randint(min_possible, max_possible)
    self.current_bet = random_bet
