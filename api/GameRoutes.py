from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.GameController import GameController


router = APIRouter()
controller = GameController()

@router.post("/session/{session_id}/game/start")
async def start_game(session_id: str) -> JSONResponse:
  return await controller.start_game(session_id)

@router.post("/session/{session_id}/game/bet/place/{bet}")
async def place_bet(session_id: str, bet: int) -> JSONResponse:
  return await controller.place_bet(session_id, bet)

@router.post("/session/{session_id}/game/hit/{hand_index}")
async def hit(session_id: str, hand_index: int) -> JSONResponse:
  return await controller.hit(session_id, hand_index)

@router.post("/session/{session_id}/game/stand/{hand_index}")
async def stand(session_id: str, hand_index: int) -> JSONResponse:
  return await controller.stand(session_id, hand_index)

@router.get("/session/{session_id}/game/get")
async def get(session_id: str) -> JSONResponse:
  return await controller.get(session_id)

@router.get("/session/{session_id}/game/get_bankroll")
async def get_bankroll(session_id: str) -> JSONResponse:
  return await controller.get_bankroll(session_id)
