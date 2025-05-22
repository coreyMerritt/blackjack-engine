from pydantic import BaseModel
from controllers.SessionController import SessionController
from fastapi import APIRouter

router = APIRouter()
controller = SessionController()

class CreateSessionReq(BaseModel):
  deck_count: int
  ai_player_count: int
  min_bet: int
  max_bet: int

@router.post("/session/create")
async def create_session(req: CreateSessionReq):
  return await controller.create_session(
    req.deck_count,
    req.ai_player_count,
    req.min_bet,
    req.max_bet
  )
