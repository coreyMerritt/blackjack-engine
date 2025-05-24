from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.SimulationController import SimulationController
from models.api.RunSimulationReq import RunSimulationReq


router = APIRouter()
controller = SimulationController()

@router.post("/simulation/run")
async def run(req: RunSimulationReq) -> JSONResponse:
  return await controller.run(req)
