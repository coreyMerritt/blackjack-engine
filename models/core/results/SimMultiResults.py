from pydantic import BaseModel, Field

from models.core.results.SimMultiResultsMetadata import SimMultiResultsMetadata
from models.core.results.SimSingleResults import SimSingleResults


class SimMultiResults(BaseModel):
  metadata: SimMultiResultsMetadata = Field(default_factory=SimMultiResultsMetadata)
  average: SimSingleResults = Field(default_factory=SimSingleResults)
