import math
import random
from entities.Player import Player

class AiPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None):
    if bet is not None:
      assert(bet >= min_possible)
      assert(bet <= max_possible)

      self.current_bet = bet
      return 0
    
    random_bet = random.randint(min_possible, max_possible)
    self.current_bet = random_bet
    return 0