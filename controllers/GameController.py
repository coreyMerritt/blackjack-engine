from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models.api.RegisterHumanPlayerReq import RegisterHumanPlayerReq
from models.enums.GameState import GameState
from services.SessionManagerSingleton import SessionManagerSingleton


class GameController:
  __session_manager: SessionManagerSingleton

  def __init__(self):
    self.__session_manager = SessionManagerSingleton()

  async def register_human_player(self, session_id: str, req: RegisterHumanPlayerReq) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.NOT_STARTED:
      raise HTTPException(status_code=409, detail="Invalid game state")
    player_id = game.register_human_player(req.human_player_info)
    return JSONResponse(status_code=200, content={"player_id": str(player_id)})

  async def start_game(self, session_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.NOT_STARTED:
      raise HTTPException(status_code=409, detail="Invalid game state")
    game.start_game()
    return JSONResponse(status_code=200, content="Success")

  async def place_bet(self, session_id: str, player_id: str, bet: int) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.BETTING:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.place_human_player_bet(player_id, bet)
    return JSONResponse(status_code=200, content="Success")

  async def set_insurance(self, session_id: str, player_id: str, insurance: bool) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.INSURANCE:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.set_human_player_wants_insurance(player_id, insurance)
    for player in game.get_human_players():
      if player.get_hand(0).is_insured() is None:
        return JSONResponse(status_code=200, content="Success")
    game.to_next_human_state()
    return JSONResponse(status_code=200, content="Success")

  async def set_surrender(self, session_id: str, player_id: str, surrender: bool) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.LATE_SURRENDER:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.set_human_player_wants_surrender(player_id, surrender)
    for player in game.get_human_players():
      if player.get_hand(0).is_surrendered() is None:
        return JSONResponse(status_code=200, content="Success")
    game.to_next_human_state()
    return JSONResponse(status_code=200, content="Success")

  async def hit(self, session_id: str, player_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.hit_human_player(player_id)
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def stand(self, session_id: str, player_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.stand_human_player(player_id)
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def double_down(self, session_id: str, player_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.double_down_human_player(player_id)
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def split(self, session_id: str, player_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.get_state() == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")
    assert game.calculate_active_player() == game.get_player(player_id)
    game.split_human_player(player_id)
    return JSONResponse(status_code=200, content={"status": "complete"})

  async def get(self, session_id: str) -> JSONResponse:
    game = self.__session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    return JSONResponse(content=game.to_dict())
