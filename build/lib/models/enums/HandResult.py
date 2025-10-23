from enum import Enum


class HandResult(Enum):
  UNDETERMINED = 0
  BLACKJACK = 1
  WIN = 2
  LOSS = 3
  DRAW = 4
  SURRENDERED = 5
