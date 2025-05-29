from pydantic import BaseModel

from models.core.results.SimulationSingleResults import SimulationSingleResults


class SimulationMultiResultsFormatted(BaseModel):
  sims_run: int = 0
  sims_won: int = 0
  sims_lost: int = 0
  success_rate: str = ""
  risk_of_ruin: str = ""
  time_taken: str = ""
  averages: SimulationSingleResults
