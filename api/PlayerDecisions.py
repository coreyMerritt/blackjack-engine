from fastapi import APIRouter
from controllers.PlayerDecisionController import PlayerDecisionController

router = APIRouter()
controller = PlayerDecisionController()

@router.post("/session/{session_id}/decisions/hit")
async def hit(session_id: str):
  return await controller.hit(session_id)

@router.post("/session/{session_id}/decisions/stand")
async def stand(session_id: str):
  return await controller.stand(session_id)
