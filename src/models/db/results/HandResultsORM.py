from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.db.Base import Base


class HandResultsORM(Base):
  __tablename__ = "hand_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  counts_id = Column(Integer, ForeignKey("hand_results_counts.id"))
  percentages_id = Column(Integer, ForeignKey("hand_results_percentages.id"))

  counts = relationship("HandResultsCountsORM", uselist=False)
  percentages = relationship("HandResultsPercentagesORM", uselist=False)
