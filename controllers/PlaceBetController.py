from fastapi import HTTPException
from entities.Game import GameState
from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class PlaceBetController:
  async def place_bet(self, session_id: str, bet: int):
    assert isinstance(session_id, str)
    assert isinstance(bet, int)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.BETTING:
      raise HTTPException(status_code=409, detail="Invalid game state")

    game.place_bets(bet)
    game.state = GameState.DEALING
    game.deal_cards()
    game.state = GameState.HUMAN_PLAYER_DECISIONS

    return 200
