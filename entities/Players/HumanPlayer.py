from entities.Player import Player

class HumanPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None):
    assert(bet is not None)
    assert(bet >= min_possible)
    assert(bet <= max_possible)

    self.current_bet = bet
