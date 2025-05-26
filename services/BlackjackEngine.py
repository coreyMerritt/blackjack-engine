from entities.Game import Game
from models.core.DoubleDownRestrictions import DoubleDownRestrictions
from models.enums.GameState import GameState
from services.BlackjackLogger import BlackjackLogger


class BlackjackEngine():
  @staticmethod
  def place_bets(game: Game, bet: int) -> None:
    all_players = game.human_players + game.ai_players
    for player in all_players:
      player.place_bet(bet, game.rules)

  # TODO: Why is this function returning the hand value???
  @staticmethod
  def deal_cards(game: Game) -> int:
    game.state = GameState.DEALING
    full_shoe = game.dealer.shoe.full_size
    shoe_card_count = len(game.dealer.shoe.cards)
    stopping_point = full_shoe / (100 / game.dealer.shoe.reset_percentage)
    shoe_is_above_reset_point = shoe_card_count > stopping_point
    BlackjackLogger.debug(f"shoe_card_count: {shoe_card_count}")
    BlackjackLogger.debug(f"stopping_point: {stopping_point}")
    if not shoe_is_above_reset_point:
      BlackjackLogger.debug("Shuffling shoe...")
      game.dealer.load_shoe()
      game.dealer.shuffle_shoe()
    else:
      BlackjackLogger.debug("Shoe does not need to be shuffled")
    all_players = game.human_players + game.ai_players
    game.dealer.deal(all_players)

    if len(game.human_players) > 0:
      player_hand_value = game.human_players[0].get_hand_value()
      if player_hand_value != 21:
        game.state = GameState.HUMAN_PLAYER_DECISIONS
        return player_hand_value

    return 21

  @staticmethod
  def hit_first_human_player(game: Game, hand_index: int) -> None:
    human_player = game.human_players[0]
    game.dealer.hit(human_player, hand_index)

  @staticmethod
  def stand_first_human_player(game: Game, hand_index: int) -> None:
    human_player = game.human_players[0]
    game.dealer.stand(human_player, hand_index)

  # TODO: We should make this more "state aware" and callable from any state
  @staticmethod
  def finish_round(game: Game) -> None:
    game.state = GameState.AI_PLAYER_DECISIONS
    game.dealer.handle_ai_decisions(game.ai_players, game.rules)
    game.state = GameState.DEALER_DECISIONS
    game.dealer.handle_dealer_decisions()
    game.state = GameState.PAYOUTS
    all_players = game.human_players + game.ai_players
    game.dealer.handle_payouts(all_players)
    game.state = GameState.CLEANUP
    game.dealer.reset_hands(all_players)
    game.state = GameState.BETTING

  # TODO: Heck
  # @staticmethod
  # def can_double_down(double_down_restrictions: DoubleDownRestrictions, ???) -> bool:
  #   if not double_down_restrictions.allow_after_split and ???
  #   if double_down_restrictions.nine_ten_eleven_only:
  #     ???