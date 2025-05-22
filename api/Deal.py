from controllers.DealController import DealController
from fastapi import APIRouter

router = APIRouter()
controller = DealController()

@router.post("/deal/{session_id}")
async def deal(session_id: str):
    return await controller.deal(session_id)
