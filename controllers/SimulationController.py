import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class SimulationController:
  async def run(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    asyncio.create_task(simulation_engine.run())
    return JSONResponse(status_code=200, content={"status": "started"})

  async def multi_run(self, session_id: str, run_count: int) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    asyncio.create_task(simulation_engine.multi_run(run_count))
    return JSONResponse(status_code=200, content={"status": "started"})

  async def get_single_results(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = simulation_engine.get_single_results()
    return JSONResponse(content={"results": results})

  async def get_single_results_formatted(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = simulation_engine.get_single_results_formatted()
    return JSONResponse(content={"results": results})

  async def get_single_results_status(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    status = simulation_engine.get_single_results_status()
    return JSONResponse(content={"status": status})

  async def get_multi_results(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = simulation_engine.get_multi_results()
    return JSONResponse(content={"results": results})

  async def get_multi_results_formatted(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    results = simulation_engine.get_multi_results_formatted()
    return JSONResponse(content={"results": results})

  async def get_multi_results_status(self, session_id: str) -> JSONResponse:
    simulation_engine = session_manager.get_simulation(session_id)
    if not simulation_engine:
      raise HTTPException(status_code=401, detail="Invalid session")

    status = simulation_engine.get_multi_results_status()
    return JSONResponse(content={"status": status})
