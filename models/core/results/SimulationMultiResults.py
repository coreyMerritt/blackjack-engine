from pydantic import BaseModel, Field

from models.core.results.SimulationMultiResultsMetadata import SimulationMultiResultsMetadata
from models.core.results.SimulationSingleResults import SimulationSingleResults


class SimulationMultiResults(BaseModel):
  metadata: SimulationMultiResultsMetadata = Field(default_factory=SimulationMultiResultsMetadata)
  average: SimulationSingleResults = Field(default_factory=SimulationSingleResults)
