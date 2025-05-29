from pydantic import BaseModel

from models.core.results.SimulationSingleResultsFormatted import SimulationSingleResultsFormatted


class SimulationSingleResultsFormattedRes(BaseModel):
  results: SimulationSingleResultsFormatted
