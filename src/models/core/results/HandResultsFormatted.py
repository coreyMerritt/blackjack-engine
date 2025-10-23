from pydantic import BaseModel, Field

from models.core.results.HandResultsCountsFormatted import HandResultsCountsFormatted
from models.core.results.HandResultsPercentagesFormatted import HandResultsPercentagesFormatted


class HandResultsFormatted(BaseModel):
  counts: HandResultsCountsFormatted = Field(default_factory=HandResultsCountsFormatted)
  percentages: HandResultsPercentagesFormatted = Field(default_factory=HandResultsPercentagesFormatted)
