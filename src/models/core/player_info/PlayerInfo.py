from pydantic import BaseModel


class PlayerInfo(BaseModel):
  bankroll: float
