# pylint: disable=redefined-outer-name

import json
import pytest
import pytest_asyncio
from fastapi.responses import JSONResponse
from controllers.SessionController import SessionController
from models.api.CreateGameReq import CreateGameReq
from models.api.CreateSingleSimReq import CreateSingleSimReq
from models.core.rules.GameRules import GameRules
from models.core.rules.BettingRules import BettingRules
from models.core.rules.DealerRules import DealerRules
from models.core.rules.DoubleDownRules import DoubleDownRules
from models.core.rules.SplittingRules import SplittingRules
from models.core.rules.SurrenderRules import SurrenderRules
from models.core.player_info.HumanPlayerInfo import HumanPlayerInfo
from models.core.player_info.AiPlayerInfo import AiPlayerInfo
from models.core.BetSpread import BetSpread
from models.core.HumanTime import HumanTime
from models.core.SingleSimBounds import SingleSimBounds


@pytest_asyncio.fixture
async def controller():
  return SessionController()

@pytest.fixture
def valid_game_rules():
  return GameRules(
    betting_rules=BettingRules(min_bet=10, max_bet=100),
    dealer_rules=DealerRules(
      dealer_hits_soft_seventeen=True,
      deck_count=6,
      shoe_reset_percentage=50,
      blackjack_pays_multiplier=1.5
    ),
    double_down_rules=DoubleDownRules(
      double_after_hit=True,
      double_after_split_except_aces=True,
      double_after_split_including_aces=True,
      double_on_ten_eleven_only=False,
      double_on_nine_ten_eleven_only=True,
      double_on_any_two_cards=True
    ),
    splitting_rules=SplittingRules(maximum_hand_count=4, can_hit_aces=False),
    surrender_rules=SurrenderRules(early_surrender_allowed=False, late_surrender_allowed=True)
  )

@pytest.fixture
def valid_ai_info():
  return AiPlayerInfo(
    counts_cards=True,
    plays_deviations=True,
    basic_strategy_skill_level=90,
    card_counting_skill_level=85,
    deviations_skill_level=80,
    bankroll=1000,
    bet_spread=BetSpread(
      true_zero=10,
      true_one=20,
      true_two=30,
      true_three=40,
      true_four=50,
      true_five=60,
      true_six=70
    )
  )

@pytest.fixture
def valid_human_info():
  return [HumanPlayerInfo(bankroll=1000)]

@pytest.fixture
def create_game_req(valid_game_rules, valid_ai_info, valid_human_info):
  return CreateGameReq(
    rules=valid_game_rules,
    human_player_info=valid_human_info,  # now a list
    ai_player_info=[valid_ai_info]
  )

@pytest.fixture
def create_sim_req(valid_game_rules, valid_ai_info):
  return CreateSingleSimReq(
    bounds=SingleSimBounds(bankroll_goal=2000, human_time_limit=300, sim_time_limit=60),
    time=HumanTime(hands_per_hour=300, hours_per_day=8, days_per_week=5),
    rules=valid_game_rules,
    ai_player_info=[valid_ai_info]
  )

@pytest.mark.asyncio
async def test_create_game(controller, create_game_req):
  response = await controller.create_game(create_game_req)
  assert isinstance(response, JSONResponse)
  assert response.status_code == 200
  data = json.loads(response.body)
  assert isinstance(data, str)
  assert len(data) > 0

@pytest.mark.asyncio
async def test_create_single_sim_runner(controller, create_sim_req):
  response = await controller.create_single_sim_runner(create_sim_req)
  assert isinstance(response, JSONResponse)
  assert response.status_code == 200
  data = json.loads(response.body)
  assert isinstance(data, str)
  assert len(data) > 0

@pytest.mark.asyncio
async def test_create_multi_sim_runner(controller, create_sim_req):
  response = await controller.create_multi_sim_runner(create_sim_req)
  assert isinstance(response, JSONResponse)
  assert response.status_code == 200
  data = json.loads(response.body)
  assert isinstance(data, str)
  assert len(data) > 0
