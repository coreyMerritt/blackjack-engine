from pydantic import BaseModel

from models.core.results.SimulationSingleResults import SimulationSingleResults


class SimulationSingleResultsRes(BaseModel):
  results: SimulationSingleResults
