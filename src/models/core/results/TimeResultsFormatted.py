from pydantic import BaseModel


class TimeResultsFormatted(BaseModel):
  human_time: str = ""
  simulation_time: str = ""
