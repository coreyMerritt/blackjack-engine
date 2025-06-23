from pydantic import BaseModel


class SimulationMultiResultsMetadataFormatted(BaseModel):
  sims_run: int = 0
  sims_won: int = 0
  sims_lost: int = 0
  sims_unfinished: int = 0
  success_rate: str = ""
  failure_rate: str = ""
  simulation_time: str = ""
  human_time: str = ""
