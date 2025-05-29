from pydantic import BaseModel

from models.core.results.SimulationMultiResultsFormatted import SimulationMultiResultsFormatted


class SimulationMultiResultsResFormatted(BaseModel):
  results: SimulationMultiResultsFormatted
