import uuid
from entities.Game import Game

class SessionManagerSingleton:
  _instance: "SessionManagerSingleton" = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.sessions = {}
    return cls._instance

  def create_session(self, deck_count: int, ai_player_count: int, min_bet: int, max_bet: int):
    session_id = str(uuid.uuid4())
    game = Game(deck_count, ai_player_count, min_bet, max_bet)
    self.sessions[session_id] = game
    return session_id

  def get_game(self, session_id: str):
    return self.sessions.get(session_id)
