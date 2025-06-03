from fastapi import APIRouter
from fastapi.responses import JSONResponse
from controllers.SimulationController import SimulationController


router = APIRouter()
controller = SimulationController()

@router.post("/session/{session_id}/simulation/run")
async def run(session_id: str) -> JSONResponse:
  return await controller.run(session_id)

@router.post("/session/{session_id}/simulation/run/{run_count}")
async def multi_run(session_id: str, run_count: int) -> JSONResponse:
  return await controller.multi_run(session_id, run_count)

@router.get("/session/{session_id}/simulation/results/get_single")
async def get_single_results(session_id: str) -> JSONResponse:
  return await controller.get_single_results(session_id)

@router.get("/session/{session_id}/simulation/results/get_single_formatted")
async def get_single_results_formatted(session_id: str) -> JSONResponse:
  return await controller.get_single_results_formatted(session_id)

@router.get("/session/{session_id}/simulation/results/check_single")
async def get_single_results_progress(session_id: str) -> JSONResponse:
  return await controller.get_single_results_progress(session_id)

@router.get("/session/{session_id}/simulation/results/get_multi")
async def get_multi_results(session_id: str) -> JSONResponse:
  return await controller.get_multi_results(session_id)

@router.get("/session/{session_id}/simulation/results/get_multi_formatted")
async def get_multi_results_formatted(session_id: str) -> JSONResponse:
  return await controller.get_multi_results_formatted(session_id)

@router.get("/session/{session_id}/simulation/results/check_multi")
async def get_multi_results_progress(session_id: str) -> JSONResponse:
  return await controller.get_multi_results_progress(session_id)
