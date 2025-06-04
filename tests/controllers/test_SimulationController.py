from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import pytest_asyncio
from fastapi import HTTPException
from services.SessionManagerSingleton import SessionManagerSingleton
from controllers.SimulationController import SimulationController


@pytest_asyncio.fixture
async def controller():
  return SimulationController()


@pytest.fixture
def session_id():
  return "test-session-id"


@pytest.fixture
def fake_single_sim_runner():
  runner = MagicMock()
  runner.run = AsyncMock()
  runner.get_results_progress.return_value = 42
  runner.get_results.return_value = {"some": "results"}
  runner.get_results_formatted.return_value = {"formatted": "results"}
  return runner


@pytest.fixture
def fake_multi_sim_runner():
  runner = MagicMock()
  runner.run = AsyncMock()
  runner.get_results_progress.return_value = 80
  runner.get_results.return_value = {"multi": "results"}
  runner.get_results_formatted.return_value = {"formatted": "multi results"}
  return runner


@patch.object(SessionManagerSingleton, "get_single_sim_runner")
@pytest.mark.asyncio
async def test_run_valid_session(mock_get_runner, controller, session_id, fake_single_sim_runner):
  mock_get_runner.return_value = fake_single_sim_runner
  response = await controller.run(session_id)
  assert response.status_code == 200
  assert response.body == b'{"status":"started"}'


@patch.object(SessionManagerSingleton, "get_single_sim_runner", return_value=None)
@pytest.mark.asyncio
async def test_run_invalid_session(mock_get_runner, controller, session_id):
  with pytest.raises(HTTPException) as exc_info:
    await controller.run(session_id)
  assert exc_info.value.status_code == 401


@patch.object(SessionManagerSingleton, "get_single_sim_runner")
@pytest.mark.asyncio
async def test_get_single_results_progress(mock_get_runner, controller, session_id, fake_single_sim_runner):
  mock_get_runner.return_value = fake_single_sim_runner
  response = await controller.get_single_results_progress(session_id)
  assert response.body == b'{"status":42}'


@patch.object(SessionManagerSingleton, "get_single_sim_runner")
@pytest.mark.asyncio
async def test_get_single_results(mock_get_runner, controller, session_id, fake_single_sim_runner):
  mock_get_runner.return_value = fake_single_sim_runner
  response = await controller.get_single_results(session_id)
  assert response.body == b'{"results":{"some":"results"}}'


@patch.object(SessionManagerSingleton, "get_single_sim_runner")
@pytest.mark.asyncio
async def test_get_single_results_formatted(mock_get_runner, controller, session_id, fake_single_sim_runner):
  mock_get_runner.return_value = fake_single_sim_runner
  response = await controller.get_single_results_formatted(session_id)
  assert response.body == b'{"results":{"formatted":"results"}}'


@patch.object(SessionManagerSingleton, "get_multi_sim_runner")
@pytest.mark.asyncio
async def test_multi_run_valid(mock_get_runner, controller, session_id, fake_multi_sim_runner):
  mock_get_runner.return_value = fake_multi_sim_runner
  response = await controller.multi_run(session_id, 5)
  assert response.status_code == 200
  assert response.body == b'{"status":"started"}'


@patch.object(SessionManagerSingleton, "get_multi_sim_runner")
@pytest.mark.asyncio
async def test_get_multi_results_progress(mock_get_runner, controller, session_id, fake_multi_sim_runner):
  mock_get_runner.return_value = fake_multi_sim_runner
  response = await controller.get_multi_results_progress(session_id)
  assert response.body == b'{"status":80}'


@patch.object(SessionManagerSingleton, "get_multi_sim_runner")
@pytest.mark.asyncio
async def test_get_multi_results(mock_get_runner, controller, session_id, fake_multi_sim_runner):
  mock_get_runner.return_value = fake_multi_sim_runner
  response = await controller.get_multi_results(session_id)
  assert response.body == b'{"results":{"multi":"results"}}'


@patch.object(SessionManagerSingleton, "get_multi_sim_runner")
@pytest.mark.asyncio
async def test_get_multi_results_formatted(mock_get_runner, controller, session_id, fake_multi_sim_runner):
  mock_get_runner.return_value = fake_multi_sim_runner
  response = await controller.get_multi_results_formatted(session_id)
  assert response.body == b'{"results":{"formatted":"multi results"}}'


@patch.object(SessionManagerSingleton, "get_multi_sim_runner", return_value=None)
@pytest.mark.asyncio
async def test_multi_run_invalid_session(mock_get_runner, controller, session_id):
  with pytest.raises(HTTPException):
    await controller.multi_run(session_id, 3)
