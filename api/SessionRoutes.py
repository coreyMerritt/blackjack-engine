from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.SessionController import SessionController
from controllers.SessionController import CreateGameReq
from models.api.CreateSimulationReq import CreateSimulationReq


router = APIRouter()
controller = SessionController()

@router.post("/session/game/create")
async def create_game(req: CreateGameReq) -> JSONResponse:
  return await controller.create_game(req)

@router.post("/session/simulation/create")
async def create_simulation(req: CreateSimulationReq) -> JSONResponse:
  return await controller.create_simulation(req)
