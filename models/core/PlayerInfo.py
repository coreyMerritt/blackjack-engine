from pydantic import BaseModel

class PlayerInfo(BaseModel):
  money: int
