from pydantic import BaseModel, Field

from models.core.results.SimulationSingleResults import SimulationSingleResults


class SimulationMultiResults(BaseModel):
  sims_run: int = 0
  sims_won: int = 0
  sims_lost: int = 0
  success_rate: float = 0
  risk_of_ruin: float = 0
  time_taken: float = 0
  averages: SimulationSingleResults = Field(default_factory=SimulationSingleResults)
