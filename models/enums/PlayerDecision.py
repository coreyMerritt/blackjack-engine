from enum import Enum


class PlayerDecision(Enum):
  PLACEHOLDER = 0
  HIT = 1
  STAND = 2
  DOUBLE_DOWN_HIT = 3
  DOUBLE_DOWN_STAND = 4
  SPLIT = 5
  SURRENDER = 6
