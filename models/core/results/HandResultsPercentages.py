from pydantic import BaseModel


class HandResultsPercentages(BaseModel):
  won: float = 0.0
  lost: float = 0.0
  drawn: float = 0.0
