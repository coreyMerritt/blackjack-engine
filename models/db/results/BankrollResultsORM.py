from sqlalchemy import Column, Float, Integer, JSON
from models.db.Base import Base

class BankrollResultsORM(Base):
  __tablename__ = "bankroll_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  starting = Column(Float, default=0)
  ending = Column(Float, default=0)
  total_profit = Column(Float, default=0)
  profit_from_true = Column(JSON, default=lambda: [0.0] * 7)
  profit_per_hand = Column(Float, default=0)
  profit_per_hour = Column(Float, default=0)
  peak = Column(Float, default=0)
