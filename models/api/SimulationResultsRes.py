from pydantic import BaseModel

class SimulationResults(BaseModel):
  ending_money: int
  hand_count: int
  highest_money: int
  human_time: str
  simulation_time: int
