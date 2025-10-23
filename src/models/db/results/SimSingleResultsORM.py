from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models.db.Base import Base


class SimSingleResultsORM(Base):
  __tablename__ = "simulation_single_results"

  id = Column(Integer, primary_key=True, autoincrement=True)
  hands_id = Column(Integer, ForeignKey("hand_results.id"))
  bankroll_id = Column(Integer, ForeignKey("bankroll_results.id"))
  time_id = Column(Integer, ForeignKey("time_results.id"))
  request_id = Column(Integer, ForeignKey("create_single_sim_req.id"))
  won = Column(Boolean, nullable=True)

  hands = relationship("HandResultsORM", uselist=False)
  bankroll = relationship("BankrollResultsORM", uselist=False)
  time = relationship("TimeResultsORM", uselist=False)
  request = relationship("CreateSingleSimReqORM", back_populates="results")
