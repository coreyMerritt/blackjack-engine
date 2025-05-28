from pydantic import BaseModel


class TimeResults(BaseModel):
  human_time: float
  simulation_time: float
