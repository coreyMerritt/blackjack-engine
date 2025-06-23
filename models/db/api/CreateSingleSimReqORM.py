from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.db.Base import Base

class CreateSingleSimReqORM(Base):
  __tablename__ = "create_single_sim_req"

  id = Column(Integer, primary_key=True, autoincrement=True)
  bounds_id = Column(Integer, ForeignKey("single_sim_bounds.id"))
  time_id = Column(Integer, ForeignKey("human_time.id"))
  rules_id = Column(Integer, ForeignKey("game_rules.id"))

  bounds = relationship("SingleSimBoundsORM", uselist=False)
  time = relationship("HumanTimeORM", uselist=False)
  rules = relationship("GameRulesORM", uselist=False)
  ai_player_info = relationship("AiPlayerInfoORM")
  results = relationship("SimulationSingleResultsORM", back_populates="request")
