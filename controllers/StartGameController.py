from fastapi import HTTPException
from entities.Game import GameState
from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class StartGameController:
  async def start_game(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    game.state = GameState.BETTING

    return 200
