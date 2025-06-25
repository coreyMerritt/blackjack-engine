import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, select, and_
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from models.core.results.SimulationMultiResults import SimulationMultiResults
from models.db.Base import Base
from models.api.CreateSingleSimReq import CreateSingleSimReq

from models.core.results.SimulationSingleResults import SimulationSingleResults
from models.db.api.CreateSingleSimReqORM import CreateSingleSimReqORM
from models.db.results.BankrollResultsORM import BankrollResultsORM
from models.db.results.HandResultsCountsORM import HandResultsCountsORM
from models.db.results.HandResultsORM import HandResultsORM
from models.db.results.HandResultsPercentagesORM import HandResultsPercentagesORM
from models.db.results.SimulationSingleResultsORM import SimulationSingleResultsORM
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
from services.SimulationDataTransformer import SimulationDataTransformer


class DatabaseHandler():
  __engine: Engine
  __session: Session
  __simulation_data_transformer: SimulationDataTransformer

  def __init__(self):
    _ = PlayerInfoORM  # noqa: F401]
    user = os.getenv("BJE_MYSQL_USER")

    password = quote_plus(os.getenv("BJE_MYSQL_PASS", ""))
    host = os.getenv("BJE_MYSQL_HOST")
    port = os.getenv("BJE_MYSQL_PORT")
    db_name = os.getenv("BJE_MYSQL_DB_NAME")
    if user is None or password is None or host is None or port is None or db_name is None:
      raise RuntimeError(
        "BJE_MYSQL_USER, BJE_MYSQL_PASS, BJE_MYSQL_HOST, BJE_MYSQL_PORT, or BJE_MYSQL_DB_NAME are not in env."
      )
    db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    self.__engine = create_engine(db_url, echo=False)
    self.__session_local = sessionmaker(bind=self.__engine)
    self.__session: Session = self.__session_local()
    self.__simulation_data_transformer = SimulationDataTransformer()
    Base.metadata.create_all(bind=self.__engine)

  def store_simulation_single_result(
    self,
    sim_result: SimulationSingleResults,
    request: CreateSingleSimReq
  ) -> None:
    bounds_orm = SingleSimBoundsORM(**request.bounds.model_dump())
    time_orm = HumanTimeORM(**request.time.model_dump())

    betting_orm = BettingRulesORM(**request.rules.betting_rules.model_dump())
    dealer_orm = DealerRulesORM(**request.rules.dealer_rules.model_dump())
    double_orm = DoubleDownRulesORM(**request.rules.double_down_rules.model_dump())
    splitting_orm = SplittingRulesORM(**request.rules.splitting_rules.model_dump())
    surrender_orm = SurrenderRulesORM(**request.rules.surrender_rules.model_dump())

    rules_orm = GameRulesORM(
      betting_rules=betting_orm,
      dealer_rules=dealer_orm,
      double_down_rules=double_orm,
      splitting_rules=splitting_orm,
      surrender_rules=surrender_orm
    )

    ai_player_info_orm_list = []
    for ai in request.ai_player_info:
      spread = BetSpreadORM(**ai.bet_spread.model_dump())
      self.__session.add(spread)
      ai_player = AiPlayerInfoORM(
        bankroll=ai.bankroll,
        counts_cards=ai.counts_cards,
        plays_deviations=ai.plays_deviations,
        basic_strategy_skill_level=ai.basic_strategy_skill_level,
        card_counting_skill_level=ai.card_counting_skill_level,
        deviations_skill_level=ai.deviations_skill_level,
        bet_spread=spread
      )
      self.__session.add(ai_player)
      ai_player_info_orm_list.append(ai_player)

    self.__session.add_all([
      bounds_orm, time_orm,
      betting_orm, dealer_orm, double_orm,
      splitting_orm, surrender_orm,
      rules_orm
    ])
    self.__session.flush()

    request_orm = CreateSingleSimReqORM(
      bounds=bounds_orm,
      time=time_orm,
      rules=rules_orm,
      ai_player_info=ai_player_info_orm_list
    )
    self.__session.add(request_orm)
    self.__session.flush()

    counts_orm = HandResultsCountsORM(**sim_result.hands.counts.model_dump())
    percentages_orm = HandResultsPercentagesORM(**sim_result.hands.percentages.model_dump())
    hands_orm = HandResultsORM(counts=counts_orm, percentages=percentages_orm)
    bankroll_orm = BankrollResultsORM(**sim_result.bankroll.model_dump())
    time_orm_result = TimeResultsORM(**sim_result.time.model_dump())

    self.__session.add_all([
      counts_orm, percentages_orm, hands_orm,
      bankroll_orm, time_orm_result
    ])
    self.__session.flush()

    sim_orm = SimulationSingleResultsORM(
      won=sim_result.won,
      hands=hands_orm,
      bankroll=bankroll_orm,
      time=time_orm_result,
      request=request_orm
    )
    self.__session.add(sim_orm)
    try:
      self.__session.commit()
    except Exception:
      self.__session.rollback()

  def get_all_sim_results(
    self,
    request: CreateSingleSimReq
  ) -> SimulationMultiResults | None:
    bounds_data = request.bounds.model_dump()
    time_data = request.time.model_dump()
    rules = request.rules
    betting = rules.betting_rules.model_dump()
    dealer = rules.dealer_rules.model_dump()
    double = rules.double_down_rules.model_dump()
    splitting = rules.splitting_rules.model_dump()
    surrender = rules.surrender_rules.model_dump()
    ai_info_dicts = [ai.model_dump() for ai in request.ai_player_info]

    query = (
      self.__session.query(CreateSingleSimReqORM.id)
      .join(CreateSingleSimReqORM.bounds).filter_by(**bounds_data)
      .join(CreateSingleSimReqORM.time).filter_by(**time_data)
      .join(CreateSingleSimReqORM.rules)
      .join(GameRulesORM.betting_rules).filter_by(**betting)
      .join(GameRulesORM.dealer_rules).filter_by(**dealer)
      .join(GameRulesORM.double_down_rules).filter_by(**double)
      .join(GameRulesORM.splitting_rules).filter_by(**splitting)
      .join(GameRulesORM.surrender_rules).filter_by(**surrender)
    )

    for ai_dict in ai_info_dicts:
      bet_spread_dict = ai_dict.pop("bet_spread", {})
      query = query.filter(
        CreateSingleSimReqORM.ai_player_info.any(
          and_(
            *(getattr(AiPlayerInfoORM, k) == v for k, v in ai_dict.items()),
            AiPlayerInfoORM.bet_spread.has(**bet_spread_dict)
          )
        )
      )

    subq = query.subquery()

    sim_results = (
      self.__session.query(SimulationSingleResultsORM)
      .filter(SimulationSingleResultsORM.request_id.in_(select(subq.c.id)))
      .all()
    )
    sims = [self.__simulation_data_transformer.orm_to_pydantic(res) for res in sim_results]
    return self.__simulation_data_transformer.get_multi_sim_results(sims)
