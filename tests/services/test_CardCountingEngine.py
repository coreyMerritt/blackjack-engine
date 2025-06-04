import random
import pytest
from services.CardCountingEngine import CardCountingEngine


@pytest.fixture
def engine():
  return CardCountingEngine(skill_level=50)

def test_get_count_adjustment_high_accuracy(monkeypatch, engine):
  monkeypatch.setattr(random, "randint", lambda a, b: 90)
  assert engine.get_count_adjustment(2) == 1
  assert engine.get_count_adjustment(7) == 0
  assert engine.get_count_adjustment(10) == -1

def test_get_count_adjustment_medium_accuracy_to_zero(monkeypatch, engine):
  monkeypatch.setattr(random, "randint", lambda a, b: 50)
  assert engine.get_count_adjustment(3) == 0
  assert engine.get_count_adjustment(10) == 0

def test_get_count_adjustment_medium_accuracy_neutral_to_random(monkeypatch, engine):
  rolls = iter([50, 0])
  monkeypatch.setattr(random, "randint", lambda a, b: next(rolls))
  assert engine.get_count_adjustment(8) in [1, -1]

def test_get_count_adjustment_low_accuracy_flip_sign(monkeypatch, engine):
  monkeypatch.setattr(random, "randint", lambda a, b: 10)
  assert engine.get_count_adjustment(2) == -1
  assert engine.get_count_adjustment(10) == 1

def test_get_count_adjustment_low_accuracy_neutral_random(monkeypatch, engine):
  rolls = iter([10, 1])
  monkeypatch.setattr(random, "randint", lambda a, b: next(rolls))
  assert engine.get_count_adjustment(8) in [1, -1]
