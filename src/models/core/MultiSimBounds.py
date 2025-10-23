from pydantic import BaseModel


class MultiSimBounds(BaseModel):
  human_time_limit: int | None
  sim_time_limit: int | None
