from entities.Player import Player

class HumanPlayer(Player):
  def place_bet(self, min_possible, max_possible, bet=None) -> None:
    self.current_bet = bet
