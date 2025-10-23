from sqlalchemy import Boolean, Column, Integer

from models.db.Base import Base


class SplittingRulesORM(Base):
  __tablename__ = "splitting_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  maximum_hand_count = Column(Integer, nullable=False)
  can_hit_aces = Column(Boolean, nullable=False)
