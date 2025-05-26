from models.enums.Face import Face
from models.enums.Suit import Suit


class Card:
  __suit: Suit
  __face: Face
  __value: int
  __value_can_reset: bool

  def __init__(self, suit: Suit, face: Face) -> None:
    self.__suit = suit
    self.__face = face
    match self.__face.value:
      case "J":
        self.set_value(10)
      case "Q":
        self.set_value(10)
      case "K":
        self.set_value(10)
      case "A":
        self.set_value(11)
      case _:
        self.set_value(int(self.__face.value))

  def get_suit(self) -> Suit:
    return self.__suit

  def get_face(self) -> Face:
    return self.__face

  def get_value(self) -> int:
    return self.__value

  def set_value(self, value: int) -> None:
    previous_value = self.__value
    self.__value = value
    if previous_value == 11 and value == 1:
      self.set_value_can_reset(False)

    if value == 1:
      self.set_value_can_reset(True)

  def set_value_can_reset(self, value_can_reset: bool) -> None:
    self.__value_can_reset = value_can_reset

  def value_can_reset(self) -> bool:
    return self.__value_can_reset

  def to_dict(self) -> dict:
    return {
      "suit": self.__suit.value,
      "face": self.__face.value,
      "value": self.__value
    }
