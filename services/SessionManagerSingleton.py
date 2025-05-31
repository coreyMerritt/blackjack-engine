from typing import List
import uuid
from entities.Game import Game
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from services.SimulationEngine import SimulationEngine

class SessionManagerSingleton:
  _instance: "SessionManagerSingleton" = None
  game_sessions: dict
  simulation_sessions: dict

  def __new__(cls) -> "SessionManagerSingleton":
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance.game_sessions = {}
      cls._instance.simulation_sessions = {}
    return cls._instance

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
    self.game_sessions[session_id] = game
    return session_id

  def create_simulation(
    self,
    rules: GameRules,
    ai_player_info: List[AiPlayerInfo],
    bankroll_goal: int,
    human_time_limit: int | None,
    sim_time_limit: int | None
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(
      rules,
      None,
      ai_player_info
    )
    simulation_engine = SimulationEngine(game, bankroll_goal, human_time_limit, sim_time_limit)
    self.simulation_sessions[session_id] = simulation_engine
    return session_id

  def get_game(self, session_id: str) -> Game:
    return self.game_sessions.get(session_id)

  def get_simulation(self, session_id: str) -> SimulationEngine:
    return self.simulation_sessions.get(session_id)
