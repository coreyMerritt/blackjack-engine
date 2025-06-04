from fastapi.responses import JSONResponse
from models.api.CreateGameReq import CreateGameReq
from models.api.CreateSimulationReq import CreateSimulationReq
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SessionController:
  async def create_game(self, req: CreateGameReq) -> JSONResponse:
    session_id = session_manager.create_game(
      req.rules,
      req.human_player_info,
      req.ai_player_info
    )

    return JSONResponse(content=session_id)

  async def create_single_sim_runner(self, req: CreateSimulationReq) -> JSONResponse:
    session_id = session_manager.create_single_sim_runner(
      req.bounds,
      req.time,
      req.rules,
      req.ai_player_info
    )

    return JSONResponse(content=session_id)

  async def create_multi_sim_runner(self, req: CreateSimulationReq) -> JSONResponse:
    session_id = session_manager.create_multi_sim_runner(
      req.bounds,
      req.time,
      req.rules,
      req.ai_player_info
    )

    return JSONResponse(content=session_id)
