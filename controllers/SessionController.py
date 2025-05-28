from fastapi.responses import JSONResponse
from models.api.CreateSessionReq import CreateSessionReq
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SessionController:
  async def create_session(self, req: CreateSessionReq) -> JSONResponse:
    session_id = session_manager.create_session(
      req.rules,
      req.human_player_info,
      req.ai_player_info
    )

    return JSONResponse(content=session_id)
