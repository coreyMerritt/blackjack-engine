from pydantic import BaseModel


class SimulationBounds(BaseModel):
  bankroll_goal: int | None
  human_time_limit: int | None
  sim_time_limit: int | None
