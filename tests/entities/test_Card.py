import pytest
from models.enums.Face import Face
from models.enums.Suit import Suit
from entities.Card import Card


@pytest.mark.parametrize("face,expected_value", [
  (Face.TWO, 2),
  (Face.THREE, 3),
  (Face.FOUR, 4),
  (Face.FIVE, 5),
  (Face.SIX, 6),
  (Face.SEVEN, 7),
  (Face.EIGHT, 8),
  (Face.NINE, 9),
  (Face.TEN, 10),
  (Face.JACK, 10),
  (Face.QUEEN, 10),
  (Face.KING, 10),
  (Face.ACE, 11),
])
def test_card_value_assignment(face, expected_value):
  card = Card(Suit.SPADES, face)
  assert card.get_value() == expected_value


def test_card_getters():
  card = Card(Suit.HEARTS, Face.FIVE)
  assert card.get_suit() == Suit.HEARTS
  assert card.get_face() == Face.FIVE
  assert card.get_value() == 5


def test_calculate_if_value_can_reset_true():
  card = Card(Suit.CLUBS, Face.ACE)
  assert card.calculate_if_value_can_reset() is True


def test_calculate_if_value_can_reset_false():
  card = Card(Suit.CLUBS, Face.KING)
  assert card.calculate_if_value_can_reset() is False


def test_set_value_changes_value():
  card = Card(Suit.DIAMONDS, Face.ACE)
  card.set_value(1)
  assert card.get_value() == 1
  assert card.calculate_if_value_can_reset() is False


def test_to_dict():
  card = Card(Suit.HEARTS, Face.TEN)
  expected = {
    "suit": Suit.HEARTS.value,
    "face": Face.TEN.value,
    "value": 10
  }
  assert card.to_dict() == expected
