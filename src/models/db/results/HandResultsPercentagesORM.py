from sqlalchemy import Column, Float, Integer
from models.db.Base import Base

class HandResultsPercentagesORM(Base):
  __tablename__ = "hand_results_percentages"

  id = Column(Integer, primary_key=True, autoincrement=True)
  blackjack = Column(Float, default=0.0)
  won = Column(Float, default=0.0)
  drawn = Column(Float, default=0.0)
  lost = Column(Float, default=0.0)
  surrendered = Column(Float, default=0.0)
