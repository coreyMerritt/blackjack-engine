from fastapi import APIRouter
from controllers.GameController import GameController

router = APIRouter()
controller = GameController()

@router.post("/session/{session_id}/game/start")
async def start_game(session_id: str):
  return await controller.start_game(session_id)

@router.post("/session/{session_id}/game/bet/place/{bet}")
async def place_bet(session_id: str, bet: int):
  return await controller.place_bet(session_id, bet)

@router.post("/session/{session_id}/game/hit")
async def hit(session_id: str):
  return await controller.hit(session_id)

@router.post("/session/{session_id}/game/stand")
async def stand(session_id: str):
  return await controller.stand(session_id)
