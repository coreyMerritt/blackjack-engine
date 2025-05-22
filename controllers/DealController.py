from fastapi import HTTPException
from entities.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class DealController:
  async def deal(self, session_id: str):
    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    return game.dealer.deal([game.human_player, *game.ai_players, game.dealer])
