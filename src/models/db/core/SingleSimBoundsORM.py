from sqlalchemy import Column, Integer
from models.db.Base import Base

class SingleSimBoundsORM(Base):
  __tablename__ = "single_sim_bounds"

  id = Column(Integer, primary_key=True, autoincrement=True)
  bankroll_goal = Column(Integer, nullable=True)
  bankroll_fail = Column(Integer, nullable=True)
  human_time_limit = Column(Integer, nullable=True)
  sim_time_limit = Column(Integer, nullable=True)
