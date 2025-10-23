from sqlalchemy import Boolean, Column, Integer

from models.db.Base import Base


class SurrenderRulesORM(Base):
  __tablename__ = "surrender_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  early_surrender_allowed = Column(Boolean, nullable=False)
  late_surrender_allowed = Column(Boolean, nullable=False)
