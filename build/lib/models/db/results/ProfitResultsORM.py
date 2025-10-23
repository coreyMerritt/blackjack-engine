from sqlalchemy import Column, Float, Integer, JSON
from models.db.Base import Base

class ProfitResultsORM(Base):
  __tablename__ = "profit_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  total = Column(Float, default=0)
  from_true = Column(JSON, default=lambda: [0.0] * 7)
  per_hand = Column(Float, default=0)
  per_hour = Column(Float, default=0)
