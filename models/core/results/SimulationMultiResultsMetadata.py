from pydantic import BaseModel


class SimulationMultiResultsMetadata(BaseModel):
  sims_run: int = 0
  sims_won: int = 0
  sims_lost: int = 0
  sims_unfinished: int = 0
  success_rate: float = 0
  risk_of_ruin: float = 0
  time_taken: float = 0
