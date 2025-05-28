from pydantic import BaseModel


class HandResults(BaseModel):
  count: int
  percent: float