from fastapi import HTTPException
from services.SessionManagerSingleton import SessionManagerSingleton
from services.ServerLogger import ServerLogger

session_manager = SessionManagerSingleton()

class StartGameController:
  async def start_game(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    game.start()
    ServerLogger.debug(6)

    return 200
