from fastapi import APIRouter
from fastapi.responses import JSONResponse

from controllers.ExistingDataController import ExistingDataController
from models.api.CreateSingleSimReq import CreateSingleSimReq

router = APIRouter()
controller = ExistingDataController()

@router.get("/data/single_sim/get")
async def get_single_sim_data(req: CreateSingleSimReq) -> JSONResponse:
  return await controller.get_sim_data(req)

@router.get("/data/single_sim/get_formatted")
async def get_single_sim_data_formatted(req: CreateSingleSimReq) -> JSONResponse:
  return await controller.get_sim_data_formatted(req)
