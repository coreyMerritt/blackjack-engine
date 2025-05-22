from services.SessionManagerSingleton import SessionManagerSingleton

session_manager = SessionManagerSingleton()

class SessionController:
  async def create_session(
    self,
    deck_count: int,
    ai_player_count: int,
    min_bet: int,
    max_bet: int
  ):
    assert(isinstance(deck_count, int))
    assert(isinstance(ai_player_count, int))
    assert(isinstance(min_bet, int))
    assert(isinstance(max_bet, int))

    session_id = session_manager.create_session(
      deck_count,
      ai_player_count,
      min_bet,
      max_bet
    )

    return { "session_id": session_id }
