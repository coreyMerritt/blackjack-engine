from enum import Enum


class PairSplittingDecision(Enum):
  NO = 0
  YES = 1
  IF_DOUBLE_AFTER_SPLITTING_ALLOWED = 2
