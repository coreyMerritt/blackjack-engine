# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock
import pytest
from entities.Game import Game
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds
from services.SingleSimulationRunner import SingleSimulationRunner


@pytest.fixture
def mock_game():
  game = MagicMock(spec=Game)
  ai_player = MagicMock()
  ai_player.get_bankroll.return_value = 1000
  game.get_ai_players.return_value = [ai_player]
  game.someone_has_bankroll.return_value = True
  return game

@pytest.fixture
def mock_bounds():
  return SingleSimBounds(
    bankroll_goal=1500,
    bankroll_fail=0,
    human_time_limit=3600,
    sim_time_limit=None
  )

@pytest.fixture
def mock_human_time():
  return HumanTime(
    hands_per_hour=100,
    hours_per_day=5,
    days_per_week=7
  )

@pytest.fixture
def runner(mock_game, mock_bounds, mock_human_time):
  return SingleSimulationRunner(mock_game, mock_bounds, mock_human_time)

def test_initial_bankroll_goal(runner):
  assert runner.get_bankroll_goal() == 1500

def test_get_bankroll(runner):
  assert runner.get_bankroll() == 1000

def test_results_progress_default(runner):
  assert runner.get_results_progress() == 0

def test_set_and_get_results(runner):
  dummy_results = {
    "hands": {
      "counts": {"total": 1, "won": 1, "lost": 0, "drawn": 0, "blackjack": 0},
      "percentages": {"won": 100.0, "lost": 0.0, "drawn": 0.0}
    },
    "bankroll": {
      "starting": 1000,
      "ending": 1100,
      "total_profit": 100,
      "profit_from_true": [0.0] * 7,
      "profit_per_hand": 100,
      "profit_per_hour": 10000,
      "peak": 1100
    },
    "time": {
      "human_time": 60,
      "simulation_time": 1.5
    }
  }
  runner.set_results(dummy_results)
  assert runner.get_results() == dummy_results
  formatted = runner.get_results_formatted()
  assert formatted["hands"]["counts"]["won"] == "1"
  assert formatted["bankroll"]["total_profit"] == "$100.00"
  assert formatted["time"]["human_time"].endswith("secs") or "mins" in formatted["time"]["human_time"]

def test_reset_game(runner):
  runner.reset_game()
  assert runner.get_results_progress() == 0
