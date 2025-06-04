from unittest.mock import MagicMock
import pytest
from entities.Dealer import Dealer
from models.enums.PlayerDecision import PlayerDecision
from models.core.rules.DealerRules import DealerRules


def dealer_rules(hits_soft_17=True, deck_count=1, reset_pct=50, blackjack_pays=1.5):
  rules = DealerRules(
    dealer_hits_soft_seventeen=hits_soft_17,
    deck_count=deck_count,
    shoe_reset_percentage=reset_pct,
    blackjack_pays_multiplier=blackjack_pays
  )
  return rules


def test_dealer_initialization_and_shoe_size():
  dealer = Dealer(dealer_rules())
  shoe = dealer.get_shoe()
  assert dealer.get_blackjack_pays_multiplier() == 1.5
  assert shoe.get_card_count() == shoe.get_full_size()
  assert dealer.get_full_shoe_size() == 52
  assert dealer.get_decks_remaining() == 1


def test_dealer_draw_reduces_shoe_count():
  dealer = Dealer(dealer_rules())
  initial_count = dealer.get_shoe_card_count()
  dealer.draw()
  assert dealer.get_shoe_card_count() == initial_count - 1


def test_get_facecard_returns_second_card():
  dealer = Dealer(dealer_rules())
  hand = MagicMock()
  hand.get_card.return_value = "SecondCard"
  dealer.get_hands = MagicMock(return_value=[hand])
  assert dealer.get_facecard() == "SecondCard"
  hand.get_card.assert_called_with(1)


@pytest.mark.parametrize("soft, expected", [
  (True, PlayerDecision.HIT),
  (False, PlayerDecision.STAND),
])
def test_dealer_hits_on_soft_17_if_rule_set(soft, expected):
  dealer = Dealer(dealer_rules(hits_soft_17=True))
  hand = MagicMock()
  hand.is_soft.return_value = soft
  dealer.get_hand_value = MagicMock(return_value=17)
  dealer.get_hands = MagicMock(return_value=[hand])

  assert dealer.get_decision() == expected


def test_dealer_stands_on_hard_17_when_hits_soft_17_is_true():
  dealer = Dealer(dealer_rules(hits_soft_17=True))
  hand = MagicMock()
  hand.is_soft.return_value = False
  dealer.get_hand_value = MagicMock(return_value=17)
  dealer.get_hands = MagicMock(return_value=[hand])
  assert dealer.get_decision() == PlayerDecision.STAND


def test_dealer_hits_below_17():
  dealer = Dealer(dealer_rules())
  dealer.get_hand_value = MagicMock(return_value=16)
  assert dealer.get_decision() == PlayerDecision.HIT


def test_dealer_stands_above_17():
  dealer = Dealer(dealer_rules())
  dealer.get_hand_value = MagicMock(return_value=18)
  assert dealer.get_decision() == PlayerDecision.STAND


def test_dealer_busts_on_hard_hand():
  dealer = Dealer(dealer_rules())
  hand = MagicMock()
  hand.get_value.return_value = 22
  hand.is_soft.return_value = False
  dealer.get_hand = MagicMock(return_value=hand)
  assert dealer.calculate_if_busted() is True


def test_dealer_does_not_bust_if_soft():
  dealer = Dealer(dealer_rules())
  hand = MagicMock()
  hand.get_value.return_value = 22
  hand.is_soft.return_value = True
  dealer.get_hand = MagicMock(return_value=hand)
  assert dealer.calculate_if_busted() is False


def test_to_dict_structure():
  dealer = Dealer(dealer_rules())
  dealer.get_hands = MagicMock(return_value=[
    MagicMock(get_cards=MagicMock(return_value=[
      MagicMock(to_dict=MagicMock(return_value={"suit": "S", "face": "A", "value": 11}))
    ]))
  ])
  result = dealer.to_dict()
  assert "shoe" in result
  assert "hand" in result
  assert isinstance(result["hand"], list)
  assert isinstance(result["shoe"], dict)
