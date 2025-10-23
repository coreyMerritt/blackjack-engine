from fastapi.responses import JSONResponse
from models.api.CreateGameReq import CreateGameReq
from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.api.CreateSingleSimReq import CreateSingleSimReq
from services.SessionManagerSingleton import SessionManagerSingleton


class SessionController:
  __session_manager: SessionManagerSingleton

  def __init__(self):
    self.__session_manager = SessionManagerSingleton()

  async def create_game(self, req: CreateGameReq) -> JSONResponse:
    session_id = self.__session_manager.create_game(
      req.rules,
      req.ai_player_info
    )

    return JSONResponse(status_code=200, content=session_id)

  async def create_single_sim_runner(self, req: CreateSingleSimReq) -> JSONResponse:
    session_id = self.__session_manager.create_single_sim_runner(
      req.bounds,
      req.time,
      req.rules,
      req.ai_player_info,
      req
    )

    return JSONResponse(status_code=200, content=session_id)

  async def create_multi_sim_runner(self, req: CreateMultiSimReq) -> JSONResponse:
    session_id = self.__session_manager.create_multi_sim_runner(
      req.multi,
      req.single.bounds,
      req.single.time,
      req.single.rules,
      req.single.ai_player_info,
      req
    )

    return JSONResponse(status_code=200, content=session_id)
