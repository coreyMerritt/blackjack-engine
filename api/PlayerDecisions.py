from fastapi import APIRouter
from controllers.PlaceBetController import PlaceBetController

router = APIRouter()
controller = PlaceBetController()

@router.post("/session/{session_id}/decisions/hit")
async def hit(session_id: str, bet: int):
  return await controller.place_bet(session_id, bet)

@router.post("/session/{session_id}/decisions/stand")
async def stand(session_id: str, bet: int):
  return await controller.place_bet(session_id, bet)
