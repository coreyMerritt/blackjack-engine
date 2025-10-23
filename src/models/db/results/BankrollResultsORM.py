from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.db.Base import Base


class BankrollResultsORM(Base):
  __tablename__ = "bankroll_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  starting = Column(Float, default=0)
  ending = Column(Float, default=0)
  highest = Column(Float, default=0)
  lowest = Column(Float, default=0)
  profit_id = Column(Integer, ForeignKey("profit_results.id"))
  profit = relationship("ProfitResultsORM", uselist=False)
