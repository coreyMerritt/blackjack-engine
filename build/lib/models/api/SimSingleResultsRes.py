from pydantic import BaseModel

from models.core.results.SimSingleResults import SimSingleResults


class SimSingleResultsRes(BaseModel):
  results: SimSingleResults
