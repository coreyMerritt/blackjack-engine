import os
import json
import hashlib
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from models.core.results.SimMultiResults import SimMultiResults
from models.db.Base import Base
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.results.SimSingleResults import SimSingleResults
from models.db.api.CreateSingleSimReqORM import CreateSingleSimReqORM
from models.db.results.BankrollResultsORM import BankrollResultsORM
from models.db.results.HandResultsCountsORM import HandResultsCountsORM
from models.db.results.HandResultsORM import HandResultsORM
from models.db.results.HandResultsPercentagesORM import HandResultsPercentagesORM
from models.db.results.ProfitResultsORM import ProfitResultsORM
from models.db.results.SimSingleResultsORM import SimSingleResultsORM
from models.db.results.TimeResultsORM import TimeResultsORM
from models.db.core.SingleSimBoundsORM import SingleSimBoundsORM
from models.db.core.HumanTimeORM import HumanTimeORM
from models.db.core.rules.GameRulesORM import GameRulesORM
from models.db.core.rules.BettingRulesORM import BettingRulesORM
from models.db.core.rules.DealerRulesORM import DealerRulesORM
from models.db.core.rules.DoubleDownRulesORM import DoubleDownRulesORM
from models.db.core.rules.SplittingRulesORM import SplittingRulesORM
from models.db.core.rules.SurrenderRulesORM import SurrenderRulesORM
from models.db.core.player_info.AiPlayerInfoORM import AiPlayerInfoORM
from models.db.core.BetSpreadORM import BetSpreadORM
from models.db.core.player_info.PlayerInfoORM import PlayerInfoORM
from services.SimDataTransformer import SimDataTransformer


class DatabaseHandler():
  __engine: Engine
  __simulation_data_transformer: SimDataTransformer

  def __init__(self):
    _ = (
      PlayerInfoORM,
      SingleSimBoundsORM,
      HumanTimeORM,
      BettingRulesORM,
      DealerRulesORM,
      DoubleDownRulesORM,
      SplittingRulesORM,
      SurrenderRulesORM,
      GameRulesORM,
      AiPlayerInfoORM,
      CreateSingleSimReqORM,
      ProfitResultsORM,
      BankrollResultsORM,
      HandResultsCountsORM,
      HandResultsPercentagesORM,
      HandResultsORM,
      TimeResultsORM,
      SimSingleResultsORM,
      BetSpreadORM,
    )
    user = os.getenv("BJE_POSTGRES_USER")
    password = quote_plus(os.getenv("BJE_POSTGRES_PASS", ""))
    host = os.getenv("BJE_POSTGRES_HOST")
    port = os.getenv("BJE_POSTGRES_PORT")
    db_name = os.getenv("BJE_POSTGRES_DB_NAME")
    if user is None or password is None or host is None or port is None or db_name is None:
      raise RuntimeError(
        "BJE_POSTGRES_USER, BJE_POSTGRES_PASS, BJE_POSTGRES_HOST, BJE_POSTGRES_PORT, or " +
        "BJE_POSTGRES_DB_NAME are not in env."
      )
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
    self.__engine = create_engine(
      db_url,
      echo=False,
      pool_size=500,
      pool_timeout=120
    )
    self.__session_maker = sessionmaker(bind=self.__engine)
    self.__simulation_data_transformer = SimDataTransformer()
    Base.metadata.create_all(bind=self.__engine)

  def store_simulation_single_result(self, sim_result: SimSingleResults, request: CreateSingleSimReq) -> None:
    session = self.__session_maker()
    try:
      request_dict = request.model_dump()
      request_json = json.dumps(request_dict, sort_keys=True)
      request_hash = hashlib.sha256(request_json.encode()).hexdigest()

      request_orm = CreateSingleSimReqORM(
        request_json=request_dict,
        request_hash=request_hash
      )
      session.add(request_orm)
      session.flush()

      counts_orm = HandResultsCountsORM(**sim_result.hands.counts.model_dump())
      percentages_orm = HandResultsPercentagesORM(**sim_result.hands.percentages.model_dump())
      hands_orm = HandResultsORM(counts=counts_orm, percentages=percentages_orm)
      profit_orm = ProfitResultsORM(**sim_result.bankroll.profit.model_dump())
      bankroll_orm = BankrollResultsORM(
          starting=sim_result.bankroll.starting,
          ending=sim_result.bankroll.ending,
          highest=sim_result.bankroll.highest,
          lowest=sim_result.bankroll.lowest,
          profit=profit_orm
      )
      time_orm_result = TimeResultsORM(**sim_result.time.model_dump())

      session.add_all([counts_orm, percentages_orm, hands_orm, bankroll_orm, time_orm_result])
      session.flush()

      sim_orm = SimSingleResultsORM(
        won=sim_result.won,
        hands=hands_orm,
        bankroll=bankroll_orm,
        time=time_orm_result,
        request=request_orm
      )
      session.add(sim_orm)
      session.commit()
    except Exception:
      session.rollback()
      raise
    finally:
      session.close()

  def get_all_sim_results(self, request: CreateSingleSimReq) -> SimMultiResults | None:
    session = self.__session_maker()
    try:
      request_dict = request.model_dump()
      request_json = json.dumps(request_dict, sort_keys=True)
      request_hash = hashlib.sha256(request_json.encode()).hexdigest()
      base_query = session.query(SimSingleResultsORM).join(SimSingleResultsORM.request)
      base_query = base_query.filter(CreateSingleSimReqORM.request_hash == request_hash)
      base_query = base_query.options(
        selectinload(SimSingleResultsORM.hands).selectinload(HandResultsORM.counts),
        selectinload(SimSingleResultsORM.hands).selectinload(HandResultsORM.percentages),
        selectinload(SimSingleResultsORM.bankroll),
        selectinload(SimSingleResultsORM.time),
      )
      results = base_query.yield_per(1000).all()
      sims = [self.__simulation_data_transformer.orm_to_pydantic(res) for res in results]
      return self.__simulation_data_transformer.get_multi_sim_results(sims)
    finally:
      session.close()
