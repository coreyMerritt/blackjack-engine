from pydantic import BaseModel

from models.core.results.SimMultiResultsFormatted import SimMultiResultsFormatted


class SimMultiResultsResFormatted(BaseModel):
  results: SimMultiResultsFormatted
