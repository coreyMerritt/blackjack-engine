from pydantic import BaseModel


class HandResults(BaseModel):
  count: int = 0
  percent: float = 0
