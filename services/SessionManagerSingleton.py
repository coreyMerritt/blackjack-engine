import uuid
from models.api.CreateSessionReq import CreateSessionReq
from entities.Game import Game

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
      deck_count,
      ai_player_count,
      min_bet,
      max_bet,
      shoe_reset_percentage,
      double_down_restrictions,
      player_info
    ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(
      deck_count,
      ai_player_count,
      min_bet,
      max_bet,
      shoe_reset_percentage,
      double_down_restrictions,
      player_info
    )
    self.sessions[session_id] = game
    return session_id

  def get_game(self, session_id: str) -> Game:
    return self.sessions.get(session_id)
