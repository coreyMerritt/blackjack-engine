from pydantic import BaseModel, Field

from models.core.results.HandResultsPercentages import HandResultsPercentages
from models.core.results.HandResultsCounts import HandResultsCounts


class HandResults(BaseModel):
  counts: HandResultsCounts = Field(default_factory=HandResultsCounts)
  percentages: HandResultsPercentages = Field(default_factory=HandResultsPercentages)
