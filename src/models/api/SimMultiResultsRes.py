from pydantic import BaseModel

from models.core.results.SimMultiResults import SimMultiResults


class SimMultiResultsRes(BaseModel):
  results: SimMultiResults
