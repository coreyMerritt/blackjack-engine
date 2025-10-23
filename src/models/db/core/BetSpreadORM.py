from sqlalchemy import Column, Float, Integer
from models.db.Base import Base

class BetSpreadORM(Base):
  __tablename__ = "bet_spread"

  id = Column(Integer, primary_key=True, autoincrement=True)
  true_zero = Column(Float, nullable=False)
  true_one = Column(Float, nullable=False)
  true_two = Column(Float, nullable=False)
  true_three = Column(Float, nullable=False)
  true_four = Column(Float, nullable=False)
  true_five = Column(Float, nullable=False)
  true_six = Column(Float, nullable=False)
