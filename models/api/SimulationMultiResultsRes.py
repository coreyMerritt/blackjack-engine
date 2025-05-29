from pydantic import BaseModel

from models.core.results.SimulationMultiResults import SimulationMultiResults


class SimulationMultiResultsRes(BaseModel):
  results: SimulationMultiResults
