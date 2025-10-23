from sqlalchemy import Column, Integer, Float
from models.db.Base import Base

class SimMultiResultsMetadataORM(Base):
  __tablename__ = "simulation_multi_results_metadata"

  id = Column(Integer, primary_key=True, autoincrement=True)
  sims_run = Column(Integer, default=0)
  sims_won = Column(Integer, default=0)
  sims_lost = Column(Integer, default=0)
  sims_unfinished = Column(Integer, default=0)
  success_rate = Column(Float, default=0)
  failure_rate = Column(Float, default=0)
  total_hands = Column(Integer, default=0)
  simulation_time = Column(Float, default=0)
  human_time = Column(Float, default=0)
