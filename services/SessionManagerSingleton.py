from typing import List
import uuid
from entities.Game import Game
from models.core.HumanTime import HumanTime
from models.core.SimulationBounds import SimulationBounds
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from services.SimulationEngine import SimulationEngine

class SessionManagerSingleton:
  _game_sessions: dict
  _simulation_sessions: dict
  __instance: "SessionManagerSingleton" = None

  def __new__(cls) -> "SessionManagerSingleton":
    if cls.__instance is None:
      cls.__instance = super().__new__(cls)
      cls.__instance._game_sessions = {}
      cls.__instance._simulation_sessions = {}
    return cls.__instance

  def create_game(
    self,
    rules: GameRules,
    human_player_info: List[HumanPlayerInfo],
    ai_player_info: List[AiPlayerInfo]
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(
      rules,
      human_player_info,
      ai_player_info
    )
    self._game_sessions[session_id] = game
    return session_id

  def create_simulation(
    self,
    bounds: SimulationBounds,
    time: HumanTime,
    rules: GameRules,
    ai_player_info: List[AiPlayerInfo]
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(
      rules,
      None,
      ai_player_info
    )
    simulation_engine = SimulationEngine(game, bounds, time)
    self._simulation_sessions[session_id] = simulation_engine
    return session_id

  def get_game(self, session_id: str) -> Game:
    return self._game_sessions.get(session_id)

  def get_simulation(self, session_id: str) -> SimulationEngine:
    return self._simulation_sessions.get(session_id)
