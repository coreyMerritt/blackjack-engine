from sqlalchemy import Column, Integer, Float
from models.db.Base import Base

class SimulationMultiResultsMetadataORM(Base):
  __tablename__ = "simulation_multi_results_metadata"

  id = Column(Integer, primary_key=True, autoincrement=True)
  sims_run = Column(Integer, default=0)
  sims_won = Column(Integer, default=0)
  sims_lost = Column(Integer, default=0)
  sims_unfinished = Column(Integer, default=0)
  success_rate = Column(Float, default=0)
  risk_of_ruin = Column(Float, default=0)
  time_taken = Column(Float, default=0)
