from fastapi.responses import JSONResponse
from models.api.CreateSingleSimReq import CreateSingleSimReq
from services.DatabaseHandler import DatabaseHandler
from services.SimDataTransformer import SimDataTransformer


class ExistingDataController():
  __database_handler: DatabaseHandler
  __simulation_data_transformer: SimDataTransformer

  def __init__(self):
    self.__database_handler = DatabaseHandler()
    self.__simulation_data_transformer = SimDataTransformer()

  async def get_sim_data(self, req: CreateSingleSimReq):
    results = self.__database_handler.get_all_sim_results(req)
    if results is None:
      return JSONResponse(status_code=200, content=None)
    return JSONResponse(status_code=200, content=results.model_dump())

  async def get_sim_data_formatted(self, req: CreateSingleSimReq):
    hours_per_day = req.time.hours_per_day
    days_per_week = req.time.days_per_week
    results = self.__database_handler.get_all_sim_results(req)
    if results is None:
      return JSONResponse(status_code=200, content=None)
    results_formatted = self.__simulation_data_transformer.format_multi_sim_results(
      results,
      hours_per_day,
      days_per_week
    )
    return JSONResponse(status_code=200, content=results_formatted.model_dump())
