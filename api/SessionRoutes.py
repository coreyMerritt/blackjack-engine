from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.SessionController import SessionController
from controllers.SessionController import CreateSessionReq


router = APIRouter()
controller = SessionController()

@router.post("/session/create")
async def create_session(req: CreateSessionReq) -> JSONResponse:
  return await controller.create_session(req)
