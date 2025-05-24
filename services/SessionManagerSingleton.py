from typing import List
import uuid
from entities.Game import Game
from models.core.AiPlayerInfo import AiPlayerInfo
from models.core.GameRules import GameRules
from models.core.HumanPlayerInfo import HumanPlayerInfo

class SessionManagerSingleton:
  _instance: "SessionManagerSingleton" = None
  sessions: dict

  def __new__(cls) -> "SessionManagerSingleton":
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.sessions = {}
    return cls._instance

  def create_session(
      self,
      rules: GameRules,
      human_player_info: List[HumanPlayerInfo],
      ai_player_info: List[AiPlayerInfo]
    ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(
      rules,
      human_player_info,
      ai_player_info
    )
    self.sessions[session_id] = game
    return session_id

  def get_game(self, session_id: str) -> Game:
    return self.sessions.get(session_id)
