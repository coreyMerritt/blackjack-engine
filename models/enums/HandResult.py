from enum import Enum


class HandResult(Enum):
  UNDETERMINED = 0
  BLACKJACK = 1
  WON = 2
  LOST = 3
  DREW = 4
