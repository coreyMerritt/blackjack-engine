from sqlalchemy import Boolean, Column, Integer

from models.db.Base import Base


class DoubleDownRulesORM(Base):
  __tablename__ = "double_down_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  double_after_hit = Column(Boolean, nullable=False)
  double_after_split_except_aces = Column(Boolean, nullable=False)
  double_after_split_including_aces = Column(Boolean, nullable=False)
  double_on_ten_eleven_only = Column(Boolean, nullable=False)
  double_on_nine_ten_eleven_only = Column(Boolean, nullable=False)
  double_on_any_two_cards = Column(Boolean, nullable=False)
