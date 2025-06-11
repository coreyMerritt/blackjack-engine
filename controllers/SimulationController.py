import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SimulationController:
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
    return JSONResponse(content={"results": results})

  async def get_single_results_formatted(self, session_id: str) -> JSONResponse:
    single_sim_runner = session_manager.get_single_sim_runner(session_id)
    if not single_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = single_sim_runner.get_results_formatted()
    return JSONResponse(content={"results": results})

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
    return JSONResponse(content={"results": results})

  async def get_multi_results_formatted(self, session_id: str) -> JSONResponse:
    multi_sim_runner = session_manager.get_multi_sim_runner(session_id)
    if not multi_sim_runner:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = multi_sim_runner.get_results_formatted()
    return JSONResponse(content={"results": results})
