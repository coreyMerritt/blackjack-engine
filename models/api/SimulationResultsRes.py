from pydantic import BaseModel

class SimulationResults(BaseModel):
  ending_money: int
  hand_count: int
  highest_money: int
  simulation_time: int
  human_time: str
