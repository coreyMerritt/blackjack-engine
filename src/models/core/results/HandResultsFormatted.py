from pydantic import BaseModel, Field

from models.core.results.HandResultsPercentagesFormatted import HandResultsPercentagesFormatted
from models.core.results.HandResultsCountsFormatted import HandResultsCountsFormatted


class HandResultsFormatted(BaseModel):
  counts: HandResultsCountsFormatted = Field(default_factory=HandResultsCountsFormatted)
  percentages: HandResultsPercentagesFormatted = Field(default_factory=HandResultsPercentagesFormatted)
