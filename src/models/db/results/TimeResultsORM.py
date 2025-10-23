from sqlalchemy import Column, Float, Integer

from models.db.Base import Base


class TimeResultsORM(Base):
  __tablename__ = "time_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  human_time = Column(Float, default=0)
  simulation_time = Column(Float, default=0)
