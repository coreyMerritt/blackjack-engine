from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models.enums.GameState import GameState
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class GameController:
  async def start_game(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    game.set_state(GameState.BETTING)
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def place_bet(self, session_id: str, bet: int) -> JSONResponse:
    assert isinstance(session_id, str)
    assert isinstance(bet, int)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.BETTING:
      raise HTTPException(status_code=409, detail="Invalid game state")

    game.place_bets(bet)
    game.deal_cards()
    JSONResponse(status_code=200, content={"status": "complete"})

  async def hit(self, session_id: str, hand_index: int) -> JSONResponse:
    assert isinstance(session_id, str)
    assert isinstance(hand_index, int)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    game.hit_player()
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def stand(self, session_id: str, hand_index: int) -> JSONResponse:
    assert isinstance(session_id, str)
    assert isinstance(hand_index, int)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    game.stand_active_hand()
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def get(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    return JSONResponse(content=game.to_dict())

  async def get_money(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    return JSONResponse(content={"money": game.human_players[0].money})
