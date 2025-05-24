from typing import List
from fastapi.responses import JSONResponse
from models.api.CreateSessionReq import CreateSessionReq
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SessionController:
  async def create_session(self, req: CreateSessionReq) -> JSONResponse:
    assert isinstance(req.rules, GameRules)
    assert isinstance(req.human_player_info, HumanPlayerInfo)
    assert isinstance(req.ai_player_info, List[AiPlayerInfo])

    session_id = session_manager.create_session(
      req.rules,
      req.human_player_info,
      req.ai_player_info
    )

    return JSONResponse(content=session_id)
