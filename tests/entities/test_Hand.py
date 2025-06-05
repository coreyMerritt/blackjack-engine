from unittest.mock import MagicMock
from entities.Card import Card
from entities.Hand import Hand
from models.enums.Face import Face
from models.enums.HandResult import HandResult
from models.enums.Suit import Suit


def mock_card(value, face=Face.FIVE, soft=False):
  card = MagicMock()
  card.get_value.return_value = value
  card.get_face.return_value = face
  card.calculate_if_value_can_reset.return_value = soft
  return card

def test_initial_state():
  cards = [mock_card(5), mock_card(6)]
  hand = Hand(cards, bet=50, from_split=True)
  assert hand.get_bet() == 50
  assert hand.get_initial_bet() == 50
  assert hand.get_insurance_bet() == 0
  assert hand.get_payout() == 0
  assert hand.is_doubled_down() is False
  assert hand.is_finalized() is False
  assert hand.is_from_split() is True
  assert hand.get_result() == HandResult.UNDETERMINED
  assert hand.get_card_count() == 2
  assert hand.get_card_value(0) == 5
  assert hand.get_card_face(1) == Face.FIVE

def test_is_soft_true_and_false():
  ace = mock_card(11, face=Face.ACE, soft=True)
  five = mock_card(5)
  hand = Hand([ace, five], 10, False)
  assert hand.is_soft() is True
  ace.get_value.return_value = 1
  assert hand.is_soft() is False

def test_get_value_with_soft_ace_adjustment():
  ace = Card(Suit.SPADES, Face.ACE)
  nine = Card(Suit.HEARTS, Face.NINE)
  king = Card(Suit.CLUBS, Face.KING)
  hand = Hand([ace, nine, king], 10, False)
  total = hand.get_value()
  assert total == 20

def test_is_pair_true_false():
  card1 = mock_card(8)
  card2 = mock_card(8)
  hand = Hand([card1, card2], 10, False)
  assert hand.is_pair() is True
  card3 = mock_card(7)
  hand2 = Hand([card1, card3], 10, False)
  assert hand2.is_pair() is False

def test_add_card_and_reset_ace_if_soft():
  ace = mock_card(11, face=Face.ACE, soft=True)
  card = mock_card(9)
  hand = Hand([ace], 10, False)
  ace.set_value = MagicMock()
  hand.add_card(card)
  assert hand.get_card_count() == 2
  ace.set_value.assert_not_called()

def test_pop_card():
  card1 = mock_card(4)
  card2 = mock_card(7)
  hand = Hand([card1, card2], 10, False)
  popped = hand.pop_card()
  assert popped == card2
  assert hand.get_card_count() == 1

def test_double_down():
  card1 = mock_card(10)
  card2 = mock_card(10)
  hand = Hand([card1, card2], 50, False)
  hand.double_down()
  assert hand.is_doubled_down() is True
  assert hand.get_bet() == 100

def test_setters_and_finalization():
  cards = [mock_card(3), mock_card(6)]
  hand = Hand(cards, 10, False)
  hand.set_bet(60)
  assert hand.get_bet() == 60
  hand.set_payout(90)
  assert hand.get_payout() == 90
  hand.set_insurance_bet(10)
  assert hand.get_insurance_bet() == 10
  assert hand.is_insured() is True
  hand.set_result(HandResult.WIN)
  assert hand.get_result() == HandResult.WIN
  assert hand.is_finalized() is True
