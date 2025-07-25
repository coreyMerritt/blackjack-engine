from typing import List
import uuid
from entities.Game import Game
from models.api.CreateMultiSimReq import CreateMultiSimReq
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.HumanTime import HumanTime
from models.core.MultiSimBounds import MultiSimBounds
from models.core.SingleSimBounds import SingleSimBounds
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.rules.GameRules import GameRules
from services.MultiSimRunner import MultiSimRunner
from services.SingleSimRunner import SingleSimRunner

class SessionManagerSingleton:
  _game_sessions: dict[str, Game]
  _single_sim_runner_sessions: dict
  _multi_sim_runner_sessions: dict
  __instance: "SessionManagerSingleton" = None # type: ignore

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
    ai_player_info: List[AiPlayerInfo]
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(rules, ai_player_info)
    self._game_sessions[session_id] = game
    return session_id

  def create_single_sim_runner(
    self,
    bounds: SingleSimBounds,
    time: HumanTime,
    rules: GameRules,
    ai_player_info: List[AiPlayerInfo],
    req: CreateSingleSimReq
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(rules, ai_player_info)
    single_sim_runner = SingleSimRunner(game, bounds, time, req)
    self._single_sim_runner_sessions[session_id] = single_sim_runner
    return session_id

  def create_multi_sim_runner(
    self,
    multi_bounds: MultiSimBounds,
    bounds: SingleSimBounds,
    time: HumanTime,
    rules: GameRules,
    ai_player_info: List[AiPlayerInfo],
    original_req: CreateMultiSimReq
  ) -> str:
    session_id = str(uuid.uuid4())
    game = Game(rules, ai_player_info)
    multi_sim_runner = MultiSimRunner(multi_bounds, game, bounds, time, original_req)
    self._multi_sim_runner_sessions[session_id] = multi_sim_runner
    return session_id

  def get_game(self, session_id: str) -> Game:
    game = self._game_sessions.get(session_id)
    if game is None:
      raise RuntimeError("Tried to retrieve a nonexistant Game session.")
    return game

  def get_single_sim_runner(self, session_id: str) -> SingleSimRunner:
    single_sim_runner = self._single_sim_runner_sessions.get(session_id)
    if single_sim_runner is None:
      raise RuntimeError("Tried to retrieve a nonexistant SingleSimRunner session.")
    return single_sim_runner

  def get_multi_sim_runner(self, session_id: str) -> MultiSimRunner:
    multi_sim_runner = self._multi_sim_runner_sessions.get(session_id)
    if multi_sim_runner is None:
      raise RuntimeError("Tried to retrieve a nonexistant MultiSimRunner session.")
    return multi_sim_runner
