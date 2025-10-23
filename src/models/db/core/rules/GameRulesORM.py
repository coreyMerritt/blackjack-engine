from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.db.Base import Base

class GameRulesORM(Base):
  __tablename__ = "game_rules"

  id = Column(Integer, primary_key=True, autoincrement=True)
  betting_rules_id = Column(Integer, ForeignKey("betting_rules.id"))
  dealer_rules_id = Column(Integer, ForeignKey("dealer_rules.id"))
  double_down_rules_id = Column(Integer, ForeignKey("double_down_rules.id"))
  splitting_rules_id = Column(Integer, ForeignKey("splitting_rules.id"))
  surrender_rules_id = Column(Integer, ForeignKey("surrender_rules.id"))

  betting_rules = relationship("BettingRulesORM", uselist=False)
  dealer_rules = relationship("DealerRulesORM", uselist=False)
  double_down_rules = relationship("DoubleDownRulesORM", uselist=False)
  splitting_rules = relationship("SplittingRulesORM", uselist=False)
  surrender_rules = relationship("SurrenderRulesORM", uselist=False)
