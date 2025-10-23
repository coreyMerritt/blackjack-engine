from pydantic import BaseModel


class SimMultiResultsMetadataFormatted(BaseModel):
  sims_run: str = ""
  sims_won: str = ""
  sims_lost: str = ""
  sims_unfinished: str = ""
  success_rate: str = ""
  failure_rate: str = ""
  total_hands: str = ""
  simulation_time: str = ""
  human_time: str = ""
