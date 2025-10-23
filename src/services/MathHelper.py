from numba import njit


@njit
def get_human_time(total_hands_played: int, hands_per_hour: int) -> float:
  hours = total_hands_played / hands_per_hour
  minutes = hours * 60
  seconds = minutes * 60
  return seconds

@njit
def get_percentage(value: float, total: float) -> float:
  if total == 0:
    return 100.0
  return (value / total) * 100.0
