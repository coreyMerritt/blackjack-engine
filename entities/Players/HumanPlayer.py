from entities.Player import Player


class HumanPlayer(Player):
  __wants_insurance: bool | None = None
  __wants_surrender: bool | None = None

  def wants_insurance(self) -> bool | None:
    return self.__wants_insurance

  def set_wants_insurance(self, val: bool) -> None:
    self.__wants_insurance = val

  def wants_surrender(self) -> bool | None:
    return self.__wants_surrender

  def set_wants_surrender(self, val: bool) -> None:
    self.__wants_surrender = val
