from fastapi import APIRouter
from controllers.StartGameController import StartGameController

router = APIRouter()
controller = StartGameController()

@router.post("/session/{session_id}/game/start")
async def start_game(session_id: str):
  return await controller.start_game(session_id)
