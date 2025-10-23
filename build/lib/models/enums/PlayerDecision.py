from enum import Enum


class PlayerDecision(Enum):
  PENDING = 0
  HIT = 1
  STAND = 2
  DOUBLE_DOWN = 3
  SPLIT = 4
  SURRENDER = 5
