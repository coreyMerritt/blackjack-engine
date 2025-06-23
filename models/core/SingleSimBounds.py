from pydantic import BaseModel


class SingleSimBounds(BaseModel):
  bankroll_goal: int | None
  bankroll_fail: int | None
  human_time_limit: int | None
  sim_time_limit: int | None
