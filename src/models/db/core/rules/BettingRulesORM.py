from sqlalchemy import Column, Integer
from models.db.Base import Base

class BettingRulesORM(Base):
  __tablename__ = "betting_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  min_bet = Column(Integer, nullable=False)
  max_bet = Column(Integer, nullable=False)
