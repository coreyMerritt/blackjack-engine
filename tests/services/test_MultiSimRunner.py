# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock
import pytest
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
    bankroll_fail=50,
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

def test_initial_state(runner):
  assert runner.get_results() is None
  assert runner.get_results_progress() == 0

def test_get_human_time_calculation(runner):
  assert runner._MultiSimRunner__get_human_time(100) == 3600.0

def test_get_time_formatted_seconds(runner):
  assert runner._MultiSimRunner__get_time_formatted(45) == "45.00 secs"

def test_set_results(runner):
  sim_data = [runner._MultiSimRunner__single_sim_runner.get_results()] * 3
  meta = {
    "sims_run": 3,
    "sims_won": 2,
    "sims_lost": 1,
    "sims_unfinished": 0,
    "success_rate": 66.67,
    "failure_rate": 33.33,
    "simulation_time": 3.2,
    "human_tume": 2.4
  }
  runner._MultiSimRunner__set_results(sim_data, meta)
  results = runner.get_results()
  assert results["sims_run"] == 3
  assert results["single_sim_averages"]["bankroll"]["total_profit"] == 200.0

def test_count_sim_won(runner):
  sims = {"run": 0, "won": 0, "lost": 0, "unfinished": 0}
  runner._MultiSimRunner__count_sim(sims)
  assert sims["won"] == 1
  assert sims["run"] == 1

def test_get_results_formatted(runner):
  sim_data = [runner._MultiSimRunner__single_sim_runner.get_results()] * 2
  meta = {
    "sims_run": 2,
    "sims_won": 1,
    "sims_lost": 1,
    "sims_unfinished": 0,
    "success_rate": 50.0,
    "failure_rate": 50.0,
    "simulation_time": 10.0,
    "human_time": 8.7
  }
  runner._MultiSimRunner__set_results(sim_data, meta)
  formatted = runner.get_results_formatted()
  assert formatted["multi_sim_info"]["sims_run"] == "2"
  assert formatted["multi_sim_info"]["success_rate"] == "50.00%"
  assert "single_sim_averages" in formatted
