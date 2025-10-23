from sqlalchemy import Column, Integer

from models.db.Base import Base


class HandResultsCountsORM(Base):
  __tablename__ = "hand_results_counts"

  id = Column(Integer, primary_key=True, autoincrement=True)
  total = Column(Integer, default=0)
  blackjack = Column(Integer, default=0)
  won = Column(Integer, default=0)
  drawn = Column(Integer, default=0)
  lost = Column(Integer, default=0)
  surrendered = Column(Integer, default=0)
