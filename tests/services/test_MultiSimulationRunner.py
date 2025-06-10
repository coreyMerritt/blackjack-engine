# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock
import pytest
from services.MultiSimulationRunner import MultiSimulationRunner
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds
from entities.Game import Game


@pytest.fixture
def mock_game():
  return MagicMock(spec=Game)

@pytest.fixture
def mock_bounds():
  return SingleSimBounds(
    bankroll_goal=1000,
    human_time_limit=3600,
    sim_time_limit=60
  )

@pytest.fixture
def mock_human_time():
  return HumanTime(
    hands_per_hour=100,
    hours_per_day=5,
    days_per_week=7
  )

@pytest.fixture
def runner(monkeypatch, mock_game, mock_bounds, mock_human_time):
  mock_runner = MagicMock()
  mock_runner.get_bankroll.return_value = 1200
  mock_runner.get_bankroll_goal.return_value = 1000
  mock_runner.get_results.return_value = {
    "hands": {
      "counts": {"total": 10, "won": 5, "lost": 3, "drawn": 2, "blackjack": 1},
      "percentages": {"won": 50.0, "lost": 30.0, "drawn": 20.0}
    },
    "bankroll": {
      "starting": 1000,
      "ending": 1200,
      "total_profit": 200,
      "profit_from_true": [10, 20, 30, 40, 50, 60, 70],
      "profit_per_hand": 20,
      "profit_per_hour": 100,
      "peak": 1250
    },
    "time": {
      "human_time": 60,
      "simulation_time": 1.0
    },
    "total_hands_played": 10
  }
  monkeypatch.setattr("services.MultiSimulationRunner.SingleSimulationRunner", lambda *a, **kw: mock_runner)
  return MultiSimulationRunner(mock_game, mock_bounds, mock_human_time)

def test_initial_state(runner):
  assert runner.get_results() is None
  assert runner.get_results_progress() == 0

def test_get_human_time_calculation(runner):
  assert runner._MultiSimulationRunner__get_human_time(100) == 3600.0

def test_get_time_formatted_seconds(runner):
  assert runner._MultiSimulationRunner__get_time_formatted(45) == "45.00 secs"

def test_set_results(runner):
  sim_data = [runner._MultiSimulationRunner__single_sim_runner.get_results()] * 3
  meta = {
    "sims_run": 3,
    "sims_won": 2,
    "sims_lost": 1,
    "sims_unfinished": 0,
    "success_rate": 66.67,
    "risk_of_ruin": 33.33,
    "time_taken": 3.2
  }
  runner._MultiSimulationRunner__set_results(sim_data, meta)
  results = runner.get_results()
  assert results["sims_run"] == 3
  assert results["single_sim_averages"]["bankroll"]["total_profit"] == 200.0

def test_count_sim_won(runner):
  sims = {"run": 0, "won": 0, "lost": 0, "unfinished": 0}
  runner._MultiSimulationRunner__count_sim(sims)
  assert sims["won"] == 1
  assert sims["run"] == 1

def test_get_results_formatted(runner):
  sim_data = [runner._MultiSimulationRunner__single_sim_runner.get_results()] * 2
  meta = {
    "sims_run": 2,
    "sims_won": 1,
    "sims_lost": 1,
    "sims_unfinished": 0,
    "success_rate": 50.0,
    "risk_of_ruin": 50.0,
    "time_taken": 10
  }
  runner._MultiSimulationRunner__set_results(sim_data, meta)
  formatted = runner.get_results_formatted()
  assert formatted["multi_sim_info"]["sims_run"] == "2"
  assert formatted["multi_sim_info"]["success_rate"] == "50.00%"
  assert "single_sim_averages" in formatted
