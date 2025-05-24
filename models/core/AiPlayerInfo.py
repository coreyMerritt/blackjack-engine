from pydantic import BaseModel

class AiPlayerInfo(BaseModel):
  money: int
  basic_strategy_skill_level: int   # 1-10
