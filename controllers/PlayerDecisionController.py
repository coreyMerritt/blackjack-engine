from fastapi import HTTPException
from fastapi.responses import JSONResponse
from entities.Game import GameState
from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class PlayerDecisionController:
  async def hit(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    human_player = game.players[0]
    game.dealer.hit(human_player)
    if human_player.get_hand_value() > 20:
      self.next_steps(game)

    return JSONResponse(content=game.players[0].get_hand_value())

  async def stand(self, session_id: str):
    assert isinstance(session_id, str)

    game = session_manager.get_game(session_id)
    if not game:
      raise HTTPException(status_code=401, detail="Invalid session")
    if not game.state == GameState.HUMAN_PLAYER_DECISIONS:
      raise HTTPException(status_code=409, detail="Invalid game state")

    self.next_steps(game)

    return JSONResponse(content=game.players[0].get_hand_value())

  def next_steps(self, game):
    game.state = GameState.AI_PLAYER_DECISIONS
    ai_players = game.players[1:]
    game.dealer.handle_ai_decisions(ai_players)
    game.state = GameState.DEALER_DECISIONS
    game.dealer.handle_dealer_decisions()
    game.state = GameState.PAYOUTS
    # TODO: Implement Payouts
