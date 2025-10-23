from pydantic import BaseModel

class PlayerInfo(BaseModel):
  bankroll: int
