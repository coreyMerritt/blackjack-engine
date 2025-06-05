# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from unittest.mock import MagicMock, patch
import pytest
from services.BasicStrategyEngine import BasicStrategyEngine
from models.enums.PlayerDecision import PlayerDecision
from models.enums.PairSplittingDecision import PairSplittingDecision
from models.enums.Face import Face


@pytest.fixture
def mock_rules_engine():
  rules_engine = MagicMock()
  rules_engine.can_late_surrender.return_value = True
  rules_engine.can_split.return_value = True
  rules_engine.can_insure.return_value = True
  rules_engine.can_double_after_split.return_value = True
  return rules_engine

@pytest.fixture
def basic_engine(mock_rules_engine):
  return BasicStrategyEngine(
    basic_strategy_skill_level=100,
    deviations_skill_level=100,
    rules_engine=mock_rules_engine
  )

@patch('models.core.BasicStrategy.BasicStrategy.surrender', {
  (0, 10, 16): True
})
def test_wants_to_surrender_returns_true(basic_engine):
  hand = MagicMock()
  hand.get_value.return_value = 16
  hand.is_soft.return_value = False
  assert basic_engine.wants_to_surrender(10, hand, 0) is True

@patch('models.core.BasicStrategy.BasicStrategy.surrender', {
  (0, 10, 16): True
})
def test_check_for_surrender_returns_true(basic_engine):
  hand = MagicMock()
  hand.get_value.return_value = 16
  hand.is_soft.return_value = False
  assert basic_engine._BasicStrategyEngine__check_for_surrender(hand, 10, 0) is True

@patch('models.core.BasicStrategy.BasicStrategy.pair_splitting', {
  (0, 10, 8): PairSplittingDecision.YES
})
def test_check_for_split_yes(basic_engine):
  hand = MagicMock()
  hand.get_value.return_value = 16
  hand.is_soft.return_value = False
  result = basic_engine._BasicStrategyEngine__check_for_split([hand], hand, 10, 0)
  assert result is True

@patch('models.core.BasicStrategy.BasicStrategy.soft_totals', {
  (0, 10, 18): [PlayerDecision.STAND]
})
def test_get_play_soft_total(basic_engine):
  hand = MagicMock()
  hand.get_value.return_value = 18
  hand.is_soft.return_value = True
  hands = [hand]
  result = basic_engine.get_play(hands, hand, 10, 0)
  assert PlayerDecision.STAND in result

@patch('models.core.BasicStrategy.BasicStrategy.hard_totals', {
  (0, 10, 16): [PlayerDecision.HIT]
})
def test_get_play_hard_total(basic_engine):
  hand = MagicMock()
  hand.get_value.return_value = 16
  hand.is_soft.return_value = False
  hands = [hand]
  result = basic_engine.get_play(hands, hand, 10, 0)
  assert PlayerDecision.HIT in result

def test_wants_insurance_false_when_not_allowed(basic_engine, mock_rules_engine):
  mock_rules_engine.can_insure.return_value = False
  result = basic_engine.wants_insurance([], Face.ACE)
  assert result is False

def test_get_some_adjusted_value_with_high_skill(basic_engine):
  result = basic_engine._BasicStrategyEngine__get_some_adjusted_value(
    skill_level=100,
    some_val=15,
    minimum=12,
    maximum=21
  )
  assert 12 <= result <= 21

def test_get_adjusted_true_count_bounds(basic_engine):
  result = basic_engine._BasicStrategyEngine__get_adjusted_true_count(3)
  assert -1 <= result <= 6
