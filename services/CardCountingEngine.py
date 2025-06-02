import random


class CardCountingEngine():
  __skill_level: int

  def __init__(self, skill_level: int):
    self.__skill_level = skill_level

  def get_count_adjustment(self, card_value: int) -> int:
    if card_value <= 6:
      actual_adjustment = 1
    elif card_value <= 9:
      actual_adjustment = 0
    else:
      actual_adjustment = -1
    adjusted_adjustment = self.__get_adjusted_count_adjustment(actual_adjustment)
    return adjusted_adjustment

  def __get_adjusted_count_adjustment(self, actual_adjustment: int) -> int:
    accuracy_roll = random.randint(self.__skill_level, 100)
    if accuracy_roll >= 66:
      return actual_adjustment
    elif accuracy_roll >= 33:
      if actual_adjustment == 1 or actual_adjustment == -1:
        return 0
      else:
        even_odd_roll = random.randint(0, 1)
        if even_odd_roll == 0:
          return 1
        else:
          return -1
    else:
      if actual_adjustment == 1:
        return -1
      elif actual_adjustment == -1:
        return 1
      else:
        even_odd_roll = random.randint(0, 1)
        if even_odd_roll == 0:
          return 1
        else:
          return -1
