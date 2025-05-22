from fastapi import APIRouter
from controllers.PlaceBetController import PlaceBetController
from services.ServerLogger import ServerLogger

router = APIRouter()
controller = PlaceBetController()

@router.post("/session/{session_id}/place_bet/{bet}")
async def place_bet(session_id: str, bet: int):
  ServerLogger.debug("test2")
  return await controller.place_bet(session_id, bet)
