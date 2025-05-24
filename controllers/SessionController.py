from fastapi.responses import JSONResponse
from models.api.CreateSessionReq import CreateSessionReq
from models.api.PlayerInfo import PlayerInfo
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SessionController:
  async def create_session(self, req: CreateSessionReq) -> JSONResponse:
    assert isinstance(req.deck_count, int)
    assert isinstance(req.ai_player_count, int)
    assert isinstance(req.min_bet, int)
    assert isinstance(req.max_bet, int)
    assert isinstance(req.shoe_reset_percentage, int)
    assert isinstance(req.player_info, PlayerInfo)

    session_id = session_manager.create_session(
      req.deck_count,
      req.ai_player_count,
      req.min_bet,
      req.max_bet,
      req.shoe_reset_percentage,
      req.player_info
    )

    return JSONResponse(content=session_id)
