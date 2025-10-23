from sqlalchemy import Column, Integer

from models.db.Base import Base


class HumanTimeORM(Base):
  __tablename__ = "human_time"

  id = Column(Integer, primary_key=True, autoincrement=True)
  hands_per_hour = Column(Integer, nullable=False)
  hours_per_day = Column(Integer, nullable=False)
  days_per_week = Column(Integer, nullable=False)
