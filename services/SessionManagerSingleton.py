from typing import List
import uuid
from entities.Game import Game
from models.core.HumanTime import HumanTime
from models.core.SimulationBounds import SimulationBounds
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from services.MultiSimulationRunner import MultiSimulationRunner
from services.SingleSimulationRunner import SingleSimulationRunner

class SessionManagerSingleton:
  _game_sessions: dict
  _single_sim_runner_sessions: dict
  _multi_sim_runner_sessions: dict
  __instance: "SessionManagerSingleton" = None

  def __new__(cls) -> "SessionManagerSingleton":
    if cls.__instance is None:
      cls.__instance = super().__new__(cls)
      cls.__instance._game_sessions = {}
      cls.__instance._single_sim_runner_sessions = {}
      cls.__instance._multi_sim_runner_sessions = {}
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

  def create_single_sim_runner(
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
    single_sim_runner = SingleSimulationRunner(game, bounds, time)
    self._single_sim_runner_sessions[session_id] = single_sim_runner
    return session_id

  def create_multi_sim_runner(
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
    multi_sim_runner = MultiSimulationRunner(game, bounds, time)
    self._multi_sim_runner_sessions[session_id] = multi_sim_runner
    return session_id

  def get_game(self, session_id: str) -> Game:
    return self._game_sessions.get(session_id)

  def get_single_sim_runner(self, session_id: str) -> SingleSimulationRunner:
    return self._single_sim_runner_sessions.get(session_id)

  def get_multi_sim_runner(self, session_id: str) -> MultiSimulationRunner:
    return self._multi_sim_runner_sessions.get(session_id)
