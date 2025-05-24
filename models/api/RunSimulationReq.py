from models.api.CreateSessionReq import CreateSessionReq
from models.core.BetSpread import BetSpread

class RunSimulationReq(CreateSessionReq):
  money_goal: int
  bet_spread: BetSpread
