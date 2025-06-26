from pydantic import BaseModel

from models.core.results.SimSingleResultsFormatted import SimSingleResultsFormatted


class SimSingleResultsFormattedRes(BaseModel):
  results: SimSingleResultsFormatted
