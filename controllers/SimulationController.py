from fastapi.responses import JSONResponse
from entities.Game import Game
from models.api.BetSpread import BetSpread
from models.api.RunSimulationReq import RunSimulationReq
from models.api.PlayerInfo import PlayerInfo
from services.SimulationEngine import SimulationEngine


class SimulationController:
  async def run(self, req: RunSimulationReq) -> JSONResponse:
    assert isinstance(req.deck_count, int)
    assert isinstance(req.ai_player_count, int)
    assert isinstance(req.min_bet, int)
    assert isinstance(req.max_bet, int)
    assert isinstance(req.shoe_reset_percentage, int)
    assert isinstance(req.money_goal, int)
    assert isinstance(req.player_info, PlayerInfo)
    assert isinstance(req.bet_spread, BetSpread)

    game = Game(
      req.deck_count,
      req.ai_player_count,
      req.min_bet,
      req.max_bet,
      req.shoe_reset_percentage,
      req.player_info
    )

    simulation_engine = SimulationEngine(game, req.bet_spread, req.money_goal)
    simulation_engine.run()
    results = simulation_engine.get_results()

    return JSONResponse(content={"results": results})
