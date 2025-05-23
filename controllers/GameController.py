from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models.enums.GameState import GameState
from services.BlackjackEngine import BlackjackEngine
from services.SessionManagerSingleton import SessionManagerSingleton


session_manager = SessionManagerSingleton()

class GameController:
  async def start_game(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    game.state = GameState.BETTING

    return JSONResponse(content={"game": game})

  async def place_bet(self, session_id: str, bet: int) -> JSONResponse:
    assert isinstance(session_id, str)
    assert isinstance(bet, int)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.BETTING:
      raise HTTPException(status_code=409, detail="Invalid game state")

    BlackjackEngine.place_bets(game, bet)
    return_hand_value = BlackjackEngine.deal_cards(game)
    BlackjackEngine.finish_round(game)

    return JSONResponse(content={"hand_value": return_hand_value})

  async def hit(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    return_hand_value = BlackjackEngine.hit_first_human_player(game)
    if return_hand_value >= 21:
      BlackjackEngine.finish_round(game)

    return JSONResponse(content={"hand_value": return_hand_value})

  async def stand(self, session_id: str) -> JSONResponse:
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    BlackjackEngine.finish_round(game)

    return JSONResponse(content={"money": game.human_players[0].money})

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
