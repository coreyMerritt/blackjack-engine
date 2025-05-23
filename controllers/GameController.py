from fastapi import HTTPException
from fastapi.responses import JSONResponse
from models.enums.GameState import GameState
from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class GameController:
  async def start_game(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")

    game.state = GameState.BETTING

    return 200

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

    return JSONResponse(content={"hand_value": game.players[0].get_hand_value()})

  async def hit(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    human_player = game.players[0]
    game.dealer.hit(human_player)
    return_hand_value = human_player.get_hand_value()

    if return_hand_value > 20:
      self._finish_round(game)

    return JSONResponse(content={"hand_value": return_hand_value})

  async def stand(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    self._finish_round(game)

    return JSONResponse(content={"money": game.players[0].money})

  async def get(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    return JSONResponse(content=game.to_dict())

  async def get_money(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    return JSONResponse(content={"money": game.players[0].money})

  def _finish_round(self, game):
    game.state = GameState.AI_PLAYER_DECISIONS
    ai_players = game.players[1:]
    game.dealer.handle_ai_decisions(ai_players)
    game.state = GameState.DEALER_DECISIONS
    game.dealer.handle_dealer_decisions()
    game.state = GameState.PAYOUTS
    game.dealer.handle_payouts(game.players)
    game.state = GameState.CLEANUP
    game.dealer.reset_hands(game.players)
    game.state = GameState.BETTING
