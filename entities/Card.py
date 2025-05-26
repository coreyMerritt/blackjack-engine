from models.enums.Face import Face
from models.enums.Suit import Suit


class Card:
  _suit: Suit
  _face: Face
  _value: int
  _value_can_reset: bool

  def __init__(self, suit: Suit, face: Face) -> None:
    self._suit = suit
    self._face = face
    self.set_value()

  def set_value(self) -> None:
    match self._face.value:
      case "J":
        self._value = 10
        self._value_can_reset = False
      case "Q":
        self._value = 10
        self._value_can_reset = False
      case "K":
        self._value = 10
        self._value_can_reset = False
      case "A":
        self._value = 11
        self._value_can_reset = True
      case _:
        self._value = int(self._face.value)
        self._value_can_reset = False

  def to_dict(self) -> dict:
    return {
      "suit": self._suit.value,
      "face": self._face.value,
      "value": self._value
    }
