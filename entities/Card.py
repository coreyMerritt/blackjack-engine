from models.enums.Face import Face
from models.enums.Suit import Suit


class Card:
  suit: Suit
  face: Face
  value: int
  value_can_reset: bool

  def __init__(self, suit: Suit, face: Face) -> None:
    self.suit = suit
    self.face = face
    self.set_value()

  def set_value(self) -> None:
    match self.face.value:
      case "J":
        self.value = 10
        self.value_can_reset = False
      case "Q":
        self.value = 10
        self.value_can_reset = False
      case "K":
        self.value = 10
        self.value_can_reset = False
      case "A":
        self.value = 11
        self.value_can_reset = True
      case _:
        self.value = int(self.face.value)
        self.value_can_reset = False

  def to_dict(self) -> dict:
    return {
      "suit": self.suit.value,
      "face": self.face.value,
      "value": self.value
    }
