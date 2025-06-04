from unittest.mock import MagicMock
import pytest
from entities.Players.AiPlayer import AiPlayer
from models.enums.PlayerDecision import PlayerDecision


@pytest.mark.parametrize("running_count, decks_remaining, expected_true_count", [
  (12, 2, 6),
  (-5, 3, -2),
  (5, 2, 2),
  (-18, 7, -3)
])
def test_calculate_true_count(running_count, decks_remaining, expected_true_count):
  ai_player_info = MagicMock()
  ai_player_info.counts_cards = True
  ai_player_info.plays_deviations = True
  ai_player_info.basic_strategy_skill_level = 1
  ai_player_info.deviations_skill_level = 1
  ai_player_info.card_counting_skill_level = 1
  ai_player_info.bet_spread = MagicMock()

  rules_engine = MagicMock()

  ai_player = AiPlayer(ai_player_info, rules_engine)
  ai_player.set_running_count(running_count)

  assert ai_player.calculate_true_count(decks_remaining) == expected_true_count


def test_update_running_count():
  ai_player_info = MagicMock()
  ai_player_info.counts_cards = True
  ai_player_info.plays_deviations = True
  ai_player_info.basic_strategy_skill_level = 1
  ai_player_info.deviations_skill_level = 1
  ai_player_info.card_counting_skill_level = 1
  ai_player_info.bet_spread = MagicMock()

  rules_engine = MagicMock()

  player = AiPlayer(ai_player_info, rules_engine)
  player._AiPlayer__card_counting_engine = MagicMock()
  player._AiPlayer__card_counting_engine.get_count_adjustment.return_value = 1
  player._AiPlayer__running_count = 0

  player.update_running_count(10)

  assert player.get_running_count() == 1


@pytest.mark.parametrize("true_count, expected_bet", [
  (1, 20),
  (2, 40),
  (3, 60),
  (4, 80),
  (5, 100),
  (6, 120),
  (0, 10),
  (-1, 10),
])
def test_calculate_bet(true_count, expected_bet):
  ai_player_info = MagicMock()
  ai_player_info.counts_cards = True
  ai_player_info.plays_deviations = True
  ai_player_info.basic_strategy_skill_level = 1
  ai_player_info.deviations_skill_level = 1
  ai_player_info.card_counting_skill_level = 1

  bet_spread = MagicMock()
  bet_spread.true_zero = 10
  bet_spread.true_one = 20
  bet_spread.true_two = 40
  bet_spread.true_three = 60
  bet_spread.true_four = 80
  bet_spread.true_five = 100
  bet_spread.true_six = 120
  ai_player_info.bet_spread = bet_spread

  rules_engine = MagicMock()
  rules_engine.get_min_bet.return_value = 10
  rules_engine.get_max_bet.return_value = 150
  rules_engine.bet_is_legal.return_value = True

  player = AiPlayer(ai_player_info, rules_engine)
  player.get_bankroll = MagicMock(return_value=200)
  player.calculate_true_count = MagicMock(return_value=true_count)

  bet = player.calculate_bet(rules_engine, decks_remaining=2)

  assert bet == expected_bet


def test_get_decisions():
  ai_player_info = MagicMock()
  ai_player_info.counts_cards = True
  ai_player_info.plays_deviations = True
  ai_player_info.basic_strategy_skill_level = 1
  ai_player_info.deviations_skill_level = 1
  ai_player_info.card_counting_skill_level = 1
  ai_player_info.bet_spread = MagicMock()

  rules_engine = MagicMock()

  player = AiPlayer(ai_player_info, rules_engine)
  player._AiPlayer__basic_strategy_engine = MagicMock()
  player._AiPlayer__basic_strategy_engine.get_play.return_value = [PlayerDecision.HIT]
  player.get_hands = MagicMock(return_value=["hand1"])
  player.calculate_true_count = MagicMock(return_value=2)

  decisions = player.get_decisions("hand1", dealer_facecard_value=10, decks_remaining=2)

  assert decisions == [PlayerDecision.HIT]
