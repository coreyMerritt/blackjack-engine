from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.db.Base import Base

class AiPlayerInfoORM(Base):
  __tablename__ = "ai_player_info"

  id = Column(Integer, primary_key=True, autoincrement=True)
  request_id = Column(Integer, ForeignKey("create_single_sim_req.id"))

  bankroll = Column(Integer, nullable=False)
  counts_cards = Column(Boolean, nullable=False)
  plays_deviations = Column(Boolean, nullable=False)
  basic_strategy_skill_level = Column(Integer, nullable=False)
  card_counting_skill_level = Column(Integer, nullable=False)
  deviations_skill_level = Column(Integer, nullable=False)
  bet_spread_id = Column(Integer, ForeignKey("bet_spread.id"))

  bet_spread = relationship("BetSpreadORM", uselist=False)
  request = relationship("CreateSingleSimReqORM", back_populates="ai_player_info")
