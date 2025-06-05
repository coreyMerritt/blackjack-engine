# pylint: disable=redefined-outer-name

from uuid import UUID
from unittest.mock import MagicMock
import pytest
from models.enums.HandResult import HandResult
from models.core.player_info.PlayerInfo import PlayerInfo
from entities.Player import Player


class ConcretePlayer(Player):
  pass

@pytest.fixture
def test_player():
  player_info = PlayerInfo(bankroll=100.0)
  return ConcretePlayer(player_info)

def test_getters_and_initial_state(test_player):
  assert isinstance(test_player.get_id(), UUID)
  assert test_player.get_bankroll() == 100.0
  assert test_player.get_hand_count() == 0
  assert test_player.get_hands() == []
  assert test_player.has_active_hand() is False

def test_add_and_get_hand(test_player):
  hand = MagicMock()
  test_player.add_new_hand(hand)
  assert test_player.get_hand_count() == 1
  assert test_player.get_hand(0) == hand

def test_set_hands(test_player):
  hand1 = MagicMock()
  hand2 = MagicMock()
  test_player.set_hands([hand1, hand2])
  assert test_player.get_hands() == [hand1, hand2]

def test_has_blackjack_true():
  hand = MagicMock()
  hand.get_card_count.return_value = 2
  hand.get_value.return_value = 21
  player_info = PlayerInfo(bankroll=100)
  test_player = ConcretePlayer(player_info)
  test_player.set_hands([hand])
  assert test_player.has_blackjack() is True

def test_has_blackjack_false():
  hand = MagicMock()
  hand.get_card_count.return_value = 2
  hand.get_value.return_value = 20
  player_info = PlayerInfo(bankroll=100)
  test_player = ConcretePlayer(player_info)
  test_player.set_hands([hand])
  assert test_player.has_blackjack() is False

def test_calculate_active_hand_returns_correct():
  hand1 = MagicMock()
  hand2 = MagicMock()
  hand1.is_finalized.return_value = True
  hand2.is_finalized.return_value = False
  hand2.get_result.return_value = HandResult.UNDETERMINED
  player_info = PlayerInfo(bankroll=100)
  test_player = ConcretePlayer(player_info)
  test_player.set_hands([hand1, hand2])
  assert test_player.calculate_active_hand() == hand2

def test_add_to_active_hand_calls_add_card():
  hand = MagicMock()
  hand.is_finalized.return_value = False
  hand.get_result.return_value = HandResult.UNDETERMINED
  player_info = PlayerInfo(bankroll=100)
  test_player = ConcretePlayer(player_info)
  test_player.set_hands([hand])
  card = MagicMock()
  test_player.add_to_active_hand(card)
  hand.add_card.assert_called_once_with(card)

def test_increment_and_decrement_bankroll(test_player):
  test_player.increment_bankroll(25)
  assert test_player.get_bankroll() == 125
  test_player.decrement_bankroll(50)
  assert test_player.get_bankroll() == 75

def test_to_dict_structure(test_player):
  card = MagicMock()
  card.to_dict.return_value = {"face": "A", "suit": "S", "value": 11}
  hand = MagicMock()
  hand.get_cards.return_value = [card]
  test_player.set_hands([hand])
  result = test_player.to_dict()
  assert "hands" in result
  assert "bankroll" in result
  assert isinstance(result["hands"], list)
  assert isinstance(result["bankroll"], float)
