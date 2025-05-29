from pydantic import BaseModel


class TimeResults(BaseModel):
  human_time: float = 0
  simulation_time: float = 0
