from typing import List
from entities.Player import Player
from entities.Dealer import Dealer
from entities.Players.AiPlayer import AiPlayer
from entities.Players.HumanPlayer import HumanPlayer
from models.api.PlayerInfo import PlayerInfo
from models.enums.GameState import GameState
from services.BlackjackLogger import blackjack_logger

class Game:
  min_bet: int
  max_bet: int
  state: GameState
  dealer: Dealer
  players: List[Player]     # Index 0 will always be the human player

  def __init__(
    self,
    deck_count: int,
    ai_player_count: int,
    min_bet: int,
    max_bet: int,
    shoe_reset_percentage: int,
    player_info: PlayerInfo
  ):
    self.players = []
    self.players.append(HumanPlayer(player_info))

    for _ in range(ai_player_count):
      ai_player = AiPlayer(player_info)   # TODO: AI players should probably get their own info
      self.players.append(ai_player)

    self.dealer = Dealer(deck_count)
    self.dealer.load_shoe()
    self.dealer.shuffle_shoe()

    self.min_bet = min_bet
    self.max_bet = max_bet
    self.dealer.shoe.reset_percentage = shoe_reset_percentage
    self.state = GameState.NOT_STARTED

  def place_bet(self, bet: int):
    # Human player bet
    self.players[0].place_bet(self.min_bet, self.max_bet, bet)

    # AI bets
    for i in range (1, len(self.players)):
      self.players[i].place_bet(self.min_bet, self.max_bet)

  def deal_cards(self):
    self.state = GameState.DEALING
    full_shoe = self.dealer.shoe.full_size
    shoe_card_count = len(self.dealer.shoe.cards)
    stopping_point = full_shoe / (100 / self.dealer.shoe.reset_percentage)
    shoe_is_above_reset_point = shoe_card_count > stopping_point
    blackjack_logger.debug(f"shoe_card_count: {shoe_card_count}")
    blackjack_logger.debug(f"stopping_point: {stopping_point}")
    if not shoe_is_above_reset_point:
      blackjack_logger.debug("Shuffling shoe...")
      self.dealer.load_shoe()
      self.dealer.shuffle_shoe()
    else:
      blackjack_logger.debug("Shoe IS above reset point")
    self.dealer.deal(self.players)

    if self.players[0].get_hand_value() < 21:
      self.state = GameState.HUMAN_PLAYER_DECISIONS
      return self.players[0].get_hand_value()

    self.finish_round()
    return 21

  def hit(self):
    human_player = self.players[0]
    self.dealer.hit(human_player)
    hand_value = human_player.get_hand_value()

    return hand_value

  def finish_round(self):
    self.state = GameState.AI_PLAYER_DECISIONS
    ai_players = self.players[1:]
    self.dealer.handle_ai_decisions(ai_players)
    self.state = GameState.DEALER_DECISIONS
    self.dealer.handle_dealer_decisions()
    self.state = GameState.PAYOUTS
    self.dealer.handle_payouts(self.players)
    self.state = GameState.CLEANUP
    self.dealer.reset_hands(self.players)
    self.state = GameState.BETTING

  def to_dict(self):
    return {
      "max_bet": self.max_bet,
      "min_bet": self.min_bet,
      "state": self.state.name,
      "dealer": self.dealer.to_dict(),
      "players": [p.to_dict() for p in self.players]
    }
