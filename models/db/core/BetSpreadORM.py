from sqlalchemy import Column, Integer
from models.db.Base import Base

class BetSpreadORM(Base):
  __tablename__ = "bet_spread"

  id = Column(Integer, primary_key=True, autoincrement=True)
  true_zero = Column(Integer, nullable=False)
  true_one = Column(Integer, nullable=False)
  true_two = Column(Integer, nullable=False)
  true_three = Column(Integer, nullable=False)
  true_four = Column(Integer, nullable=False)
  true_five = Column(Integer, nullable=False)
  true_six = Column(Integer, nullable=False)
