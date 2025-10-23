from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.SessionController import CreateGameReq, SessionController
from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.api.CreateSingleSimReq import CreateSingleSimReq

router = APIRouter()
controller = SessionController()

@router.post("/session/game/create")
async def create_game(req: CreateGameReq) -> JSONResponse:
  return await controller.create_game(req)

@router.post("/session/simulation/single/create")
async def create_single_sim_runner(req: CreateSingleSimReq) -> JSONResponse:
  return await controller.create_single_sim_runner(req)

@router.post("/session/simulation/multi/create")
async def create_multi_sim_runner(req: CreateMultiSimReq) -> JSONResponse:
  return await controller.create_multi_sim_runner(req)
