from pydantic import BaseModel

class HumanPlayerInfo(BaseModel):
  money: int
