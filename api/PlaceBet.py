from fastapi import APIRouter
from controllers.PlaceBetController import PlaceBetController

router = APIRouter()
controller = PlaceBetController()

@router.post("/session/{session_id}/place_bet/{bet}")
async def place_bet(session_id: str, bet: int):
  return await controller.place_bets(session_id, bet)
