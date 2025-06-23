import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from services.SessionManagerSingleton import SessionManagerSingleton
from services.SimulationDataTransformer import SimulationDataTransformer


session_manager = SessionManagerSingleton()

class SimulationController:
  __simulation_data_transformer: SimulationDataTransformer

  def __init__(self):
    self.__simulation_data_transformer = SimulationDataTransformer()

  async def run(self, session_id: str) -> JSONResponse:
    single_sim_runner = session_manager.get_single_sim_runner(session_id)
    if not single_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    asyncio.create_task(single_sim_runner.run())
    return JSONResponse(status_code=200, content={"status": "started"})

  async def get_single_results_progress(self, session_id: str) -> JSONResponse:
    single_sim_runner = session_manager.get_single_sim_runner(session_id)
    if not single_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    status = single_sim_runner.get_results_progress()
    return JSONResponse(content={"status": status})

  async def get_single_results(self, session_id: str) -> JSONResponse:
    single_sim_runner = session_manager.get_single_sim_runner(session_id)
    if not single_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = single_sim_runner.get_results()
    if results is None:
      return JSONResponse(content={"results": "null"})
    return JSONResponse(content={"results": results})

  async def get_single_results_formatted(self, session_id: str) -> JSONResponse:
    single_sim_runner = session_manager.get_single_sim_runner(session_id)
    if not single_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = single_sim_runner.get_results()
    if results is None:
      return JSONResponse(content={"results": "null"})

    hours_per_day = single_sim_runner.get_hours_per_day()
    days_per_week = single_sim_runner.get_days_per_week()
    results_formatted = self.__simulation_data_transformer.format_single_sim_results(
      results,
      hours_per_day,
      days_per_week
    )
    return JSONResponse(content={"results": results_formatted.model_dump()})

  async def multi_run(self, session_id: str, run_count: int) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    asyncio.create_task(multi_sim_runner.run(run_count))
    return JSONResponse(status_code=200, content={"status": "started"})

  async def benchmark(self, session_id: str, run_count: int) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    asyncio.create_task(multi_sim_runner.run_with_benchmarking(run_count))
    return JSONResponse(status_code=200, content={"status": "started"})

  async def get_multi_results_progress(self, session_id: str) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    status = multi_sim_runner.get_results_progress()
    return JSONResponse(content={"status": status})

  async def get_multi_results(self, session_id: str) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = multi_sim_runner.get_results()
    if results is not None:
      return JSONResponse(content={"results": results.model_dump()})
    return JSONResponse(content={"results": "null"})

  async def get_multi_results_formatted(self, session_id: str) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = multi_sim_runner.get_results_formatted()
    if results is not None:
      return JSONResponse(content={"results": results.model_dump()})
    return JSONResponse(content={"results": "null"})
