import pytest
from entities.Shoe import Shoe
from entities.Card import Card
from models.enums.Face import Face
from models.enums.Suit import Suit


def make_card(face: Face = Face.TWO, suit: Suit = Suit.HEARTS) -> Card:
  return Card(suit, face)


def test_shoe_initial_state():
  shoe = Shoe(deck_count=4, reset_percentage=75)
  assert shoe.get_card_count() == 0
  assert shoe.get_deck_count() == 4
  assert shoe.get_full_size() == 208
  assert shoe.get_reset_percentage() == 75


def test_add_card_and_draw():
  shoe = Shoe(deck_count=1, reset_percentage=50)
  card = make_card(Face.ACE, Suit.SPADES)
  shoe.add_card(card)
  assert shoe.get_card_count() == 1
  drawn = shoe.draw()
  assert drawn == card
  assert shoe.get_card_count() == 0


def test_set_cards():
  shoe = Shoe(deck_count=1, reset_percentage=50)
  cards = [make_card(Face.KING), make_card(Face.QUEEN)]
  shoe.set_cards(cards[:])
  assert shoe.get_card_count() == 2
  drawn_card = shoe.draw()
  assert drawn_card.to_dict() == cards[1].to_dict()


def test_shuffle_changes_order():
  shoe = Shoe(deck_count=1, reset_percentage=50)
  cards = [make_card(Face.THREE), make_card(Face.FOUR), make_card(Face.FIVE), make_card(Face.SIX)]
  shoe.set_cards(cards[:])
  shoe.shuffle()
  shuffled_cards = shoe.to_dict()["cards"]
  original_cards = [c.to_dict() for c in cards]
  assert len(shuffled_cards) == 4
  assert set(tuple(c.items()) for c in shuffled_cards) == set(tuple(c.items()) for c in original_cards)


def test_get_decks_remaining():
  shoe = Shoe(deck_count=4, reset_percentage=75)
  cards = [make_card(Face.FIVE)] * 52
  shoe.set_cards(cards)
  remaining = shoe.get_decks_remaining()
  assert remaining == pytest.approx(1.0)


def test_to_dict():
  shoe = Shoe(deck_count=1, reset_percentage=50)
  card = make_card(Face.JACK, Suit.CLUBS)
  shoe.add_card(card)
  result = shoe.to_dict()
  assert result["full_size"] == 52
  assert result["previous_deck_count"] == 1
  assert result["reset_percentage"] == 50
  assert isinstance(result["cards"], list)
  assert result["cards"][0]["face"] == "J"
  assert result["cards"][0]["suit"] == "Clubs"
  assert result["cards"][0]["value"] == 10
