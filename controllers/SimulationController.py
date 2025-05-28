from fastapi.responses import JSONResponse
from entities.Game import Game
from models.api.RunSimulationReq import RunSimulationReq
from services.SimulationEngine import SimulationEngine


class SimulationController:
  async def run(self, req: RunSimulationReq) -> JSONResponse:
    game = Game(
      req.rules,
      None,
      req.ai_player_info
    )

    simulation_engine = SimulationEngine(game, req.money_goal)
    simulation_engine.run()
    results = simulation_engine.get_results()

    return JSONResponse(content={"results": results})
