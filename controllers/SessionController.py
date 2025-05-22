from fastapi.responses import JSONResponse
from pydantic import BaseModel
from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class CreateSessionReq(BaseModel):
  deck_count: int
  ai_player_count: int
  min_bet: int
  max_bet: int
  shoe_reset_percentage: int

class SessionController:
  async def create_session(self, req: CreateSessionReq):
    assert isinstance(req.deck_count, int)
    assert isinstance(req.ai_player_count, int)
    assert isinstance(req.min_bet, int)
    assert isinstance(req.max_bet, int)
    assert isinstance(req.shoe_reset_percentage, int)

    session_id = session_manager.create_session(
      req.deck_count,
      req.ai_player_count,
      req.min_bet,
      req.max_bet,
      req.shoe_reset_percentage
    )

    return JSONResponse(content=session_id)
