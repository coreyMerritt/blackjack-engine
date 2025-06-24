from pydantic import BaseModel


class SimulationMultiResultsMetadata(BaseModel):
  sims_run: int = 0
  sims_won: int = 0
  sims_lost: int = 0
  sims_unfinished: int = 0
  success_rate: float = 0.0
  failure_rate: float = 0.0
  total_hands: int = 0
  simulation_time: float = 0.0
  human_time: float = 0.0
