from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from models.db.Base import Base


class CreateSingleSimReqORM(Base):
  __tablename__ = "create_single_sim_req"

  id = Column(Integer, primary_key=True, autoincrement=True)
  bounds_id = Column(Integer, ForeignKey("single_sim_bounds.id"))
  time_id = Column(Integer, ForeignKey("human_time.id"))
  rules_id = Column(Integer, ForeignKey("game_rules.id"))
  request_hash = Column(String, index=True, nullable=False)
  request_json = Column(JSONB, nullable=False)

  bounds = relationship("SingleSimBoundsORM", uselist=False)
  time = relationship("HumanTimeORM", uselist=False)
  rules = relationship("GameRulesORM", uselist=False)
  ai_player_info = relationship("AiPlayerInfoORM")
  results = relationship("SimSingleResultsORM", back_populates="request")
