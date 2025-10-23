from sqlalchemy import Column, Integer

from models.db.Base import Base


class PlayerInfoORM(Base):
  __tablename__ = "player_info"

  id = Column(Integer, primary_key=True, autoincrement=True)
  bankroll = Column(Integer, nullable=False)
