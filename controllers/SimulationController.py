from fastapi.responses import JSONResponse
from entities.Game import Game
from models.core.BetSpread import BetSpread
from models.api.RunSimulationReq import RunSimulationReq
from models.core.rules.GameRules import GameRules
from services.SimulationEngine import SimulationEngine


class SimulationController:
  async def run(self, req: RunSimulationReq) -> JSONResponse:
    assert isinstance(req.rules, GameRules)
    assert isinstance(req.ai_player_info, list)
    assert isinstance(req.money_goal, int)
    assert isinstance(req.bet_spread, BetSpread)

    game = Game(
      req.rules,
      None,
      req.ai_player_info
    )

    simulation_engine = SimulationEngine(game, req.bet_spread, req.money_goal)
    simulation_engine.run()
    results = simulation_engine.get_results()

    return JSONResponse(content={"results": results})
