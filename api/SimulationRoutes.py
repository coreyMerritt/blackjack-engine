from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.SimulationController import SimulationController
from models.api.CreateSimulationReq import CreateSimulationReq


router = APIRouter()
controller = SimulationController()

@router.post("/session/{session_id}/simulation/run")
async def run(req: CreateSimulationReq) -> JSONResponse:
  return await controller.run(req)

@router.post("/session/{session_id}/simulation/run/{run_count}")
async def multi_run(session_id: str, run_count: int) -> JSONResponse:
  return await controller.multi_run(session_id, run_count)

@router.get("/session/{session_id}/simulation/results/get")
async def get_results(session_id: str) -> JSONResponse:
  return await controller.get_results(session_id)

@router.get("/session/{session_id}/simulation/results/get_formatted")
async def get_results_formatted(session_id: str) -> JSONResponse:
  return await controller.get_results_formatted(session_id)

@router.get("/session/{session_id}/simulation/results/check")
async def get_results_status(session_id: str) -> JSONResponse:
  return await controller.get_results_status(session_id)
