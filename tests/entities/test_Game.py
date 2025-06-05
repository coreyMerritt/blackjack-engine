# pylint: disable=redefined-outer-name

import pytest
from entities.Game import Game
from models.core.rules.GameRules import GameRules
from models.core.rules.BettingRules import BettingRules
from models.core.rules.DealerRules import DealerRules
from models.core.rules.DoubleDownRules import DoubleDownRules
from models.core.rules.SplittingRules import SplittingRules
from models.core.rules.SurrenderRules import SurrenderRules
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.BetSpread import BetSpread
from models.enums.GameState import GameState


@pytest.fixture
def rules():
  return GameRules(
    betting_rules=BettingRules(
      min_bet=10,
      max_bet=1000
    ),
    dealer_rules=DealerRules(
      dealer_hits_soft_seventeen=True,
      blackjack_pays_multiplier=1.5,
      deck_count=1,
      shoe_reset_percentage=75
    ),
    double_down_rules=DoubleDownRules(
      double_after_hit=True,
      double_after_split_except_aces=False,
      double_after_split_including_aces=False,
      double_on_ten_eleven_only=False,
      double_on_nine_ten_eleven_only=True,
      double_on_any_two_cards=False
    ),
    splitting_rules=SplittingRules(
      maximum_hand_count=4,
      can_hit_aces=False
    ),
    surrender_rules=SurrenderRules(
      early_surrender_allowed=False,
      late_surrender_allowed=True
    )
  )

@pytest.fixture
def ai_info():
  return [
    AiPlayerInfo(
      counts_cards=True,
      plays_deviations=True,
      basic_strategy_skill_level=1,
      card_counting_skill_level=1,
      deviations_skill_level=1,
      bet_spread=BetSpread(
        true_zero=10,
        true_one=20,
        true_two=30,
        true_three=40,
        true_four=50,
        true_five=60,
        true_six=70
      ),
      bankroll=100
    )
  ]

def test_game_initial_state(rules, ai_info):
  game = Game(rules, ai_player_info=ai_info)
  assert game.get_state() == GameState.NOT_STARTED
  assert game.get_ai_players()
  assert game.get_dealer().get_shoe().get_card_count() > 0

def test_game_state_transitions(rules, ai_info):
  game = Game(rules, ai_player_info=ai_info)
  game.continue_until_state(GameState.BETTING)
  assert game.get_state() == GameState.BETTING
  game.continue_until_state(GameState.DEALING)
  assert game.get_state() == GameState.DEALING

def test_game_to_dict(rules, ai_info):
  game = Game(rules, ai_player_info=ai_info)
  result = game.to_dict()
  assert "state" in result
  assert "dealer" in result
  assert "ai_players" in result
  assert isinstance(result["ai_players"], list)

def test_someone_has_bankroll_false(rules):
  empty_ai_info = [
    AiPlayerInfo(
      counts_cards=False,
      plays_deviations=False,
      basic_strategy_skill_level=0,
      card_counting_skill_level=0,
      deviations_skill_level=0,
      bet_spread=BetSpread(
        true_zero=10,
        true_one=20,
        true_two=30,
        true_three=40,
        true_four=50,
        true_five=60,
        true_six=70
      ),
      bankroll=0
    )
  ]
  game = Game(rules, ai_player_info=empty_ai_info)
  assert not game.someone_has_bankroll()

def test_ai_player_places_bet(rules, ai_info):
  game = Game(rules, ai_player_info=ai_info)
  game.continue_until_state(GameState.DEALING)
  ai_player = game.get_ai_players()[0]
  assert ai_player.get_hand_count() == 1
  assert ai_player.get_hand(0).get_bet() > 0
