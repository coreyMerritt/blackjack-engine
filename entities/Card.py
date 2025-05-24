from models.enums.Face import Face
from models.enums.Suit import Suit


class Card:
  suit: Suit
  face: Face
  value: int

  def __init__(self, suit: Suit, face: Face) -> None:
    self.suit = suit
    self.face = face
    self.set_value()

  def set_value(self) -> None:
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

  def to_dict(self) -> dict:
    return {
      "suit": self.suit.value,
      "face": self.face.value,
      "value": self.value
    }
