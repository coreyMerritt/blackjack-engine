from enum import Enum

class Suit(Enum):
  CLUBS = "♣"
  DIAMONDS = "♦"
  HEARTS = "♥"
  SPADES = "♠"

class Face(Enum):
  TWO = "2"
  THREE = "3"
  FOUR = "4"
  FIVE = "5"
  SIX = "6"
  SEVEN = "7"
  EIGHT = "8"
  NINE = "9"
  TEN = "10"
  JACK = "J"
  QUEEN = "Q"
  KING = "K"
  ACE = "A"

class Card:
  suit: Suit
  face: Face
  value: int

  def __init__(self, suit: Suit, face: Face):
    self.suit = suit
    self.face = face
