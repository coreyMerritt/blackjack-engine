from pydantic import BaseModel, Field

from models.core.results.SimMultiResultsMetadataFormatted import SimMultiResultsMetadataFormatted
from models.core.results.SimSingleResultsFormatted import SimSingleResultsFormatted


class SimMultiResultsFormatted(BaseModel):
  metadata: SimMultiResultsMetadataFormatted = Field(default_factory=SimMultiResultsMetadataFormatted)
  average: SimSingleResultsFormatted = Field(default_factory=SimSingleResultsFormatted)
