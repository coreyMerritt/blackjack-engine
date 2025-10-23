from sqlalchemy import Column, Boolean, Integer, Float
from models.db.Base import Base

class DealerRulesORM(Base):
  __tablename__ = "dealer_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  dealer_hits_soft_seventeen = Column(Boolean, nullable=False)
  deck_count = Column(Integer, nullable=False)
  shoe_reset_percentage = Column(Integer, nullable=False)
  blackjack_pays_multiplier = Column(Float, nullable=False)
