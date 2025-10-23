from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.GameController import GameController
from models.api.RegisterHumanPlayerReq import RegisterHumanPlayerReq

router = APIRouter()
controller = GameController()

@router.post("/session/{session_id}/game/players/human/register")
async def register_human_player(session_id: str, req: RegisterHumanPlayerReq) -> JSONResponse:
  return await controller.register_human_player(session_id, req)

@router.post("/session/{session_id}/game/start")
async def start_game(session_id: str) -> JSONResponse:
  return await controller.start_game(session_id)

@router.post("/session/{session_id}/game/player/{player_id}/bet/place/{bet}")
async def place_bet(session_id: str, player_id: str, bet: int) -> JSONResponse:
  return await controller.place_bet(session_id, player_id, bet)

@router.post("/session/{session_id}/game/player/{player_id}/insurance/{insurance}")
async def set_insurance(session_id: str, player_id: str, insurance: bool) -> JSONResponse:
  return await controller.set_insurance(session_id, player_id, insurance)

@router.post("/session/{session_id}/game/player/{player_id}/surrender/{surrender}")
async def set_surrender(session_id: str, player_id: str, surrender: bool) -> JSONResponse:
  return await controller.set_surrender(session_id, player_id, surrender)

@router.post("/session/{session_id}/game/player/{player_id}/hit")
async def hit(session_id: str, player_id: str) -> JSONResponse:
  return await controller.hit(session_id, player_id)

@router.post("/session/{session_id}/game/player/{player_id}/stand")
async def stand(session_id: str, player_id: str) -> JSONResponse:
  return await controller.stand(session_id, player_id)

@router.post("/session/{session_id}/game/player/{player_id}/double_down")
async def double_down(session_id: str, player_id: str) -> JSONResponse:
  return await controller.double_down(session_id, player_id)

@router.post("/session/{session_id}/game/player/{player_id}/split")
async def split(session_id: str, player_id: str) -> JSONResponse:
  return await controller.split(session_id, player_id)

@router.get("/session/{session_id}/game/get")
async def get(session_id: str) -> JSONResponse:
  return await controller.get(session_id)
