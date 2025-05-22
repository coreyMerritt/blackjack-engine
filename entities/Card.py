from enum import Enum

class Suit(Enum):
  CLUBS = "Clubs"
  DIAMONDS = "Diamonds"
  HEARTS = "Hearts"
  SPADES = "Spades"

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
    self.set_value()

  def set_value(self):
    match self.face.value:
      case "J":
        self.value = 10
      case "Q":
        self.value = 10
      case "K":
        self.value = 10
      case "A":
        self.value = 11
      case _:
        self.value = int(self.face.value)

  def to_dict(self):
    return {
      "suit": self.suit.value,
      "face": self.face.value,
      "value": self.value
    }
