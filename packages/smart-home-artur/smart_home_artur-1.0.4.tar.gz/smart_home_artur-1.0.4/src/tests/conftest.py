import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession


import os
os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///:memory:'
os.environ['ENV'] = 'testing'

from unittest.mock import patch

# Мокаем создание engine
with patch('sqlalchemy.ext.asyncio.create_async_engine') as mock_engine:
    mock_engine.return_value = AsyncMock()
    with patch('db.session.AsyncSession') as mock_session_class:
        mock_session_class.return_value = AsyncMock()
        try:
            from main import app
            from db.session import get_db
        except Exception as e:
            print(f"Warning during import: {e}")
            # Создаем fallback app
            from fastapi import FastAPI
            app = FastAPI()

@pytest.fixture
def mock_db():
    mock = AsyncMock(spec=AsyncSession)
    
    # 🔴 УЛУЧШЕННЫЕ МОКИ: Настраиваем все необходимые методы
    mock.add = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.refresh = AsyncMock()
    mock.execute = AsyncMock()
    mock.scalar = AsyncMock()
    mock.get = AsyncMock()
    
    # 🔴 ВАЖНО: Настраиваем цепочные вызовы для execute
    mock_execute_result = AsyncMock()
    mock_execute_result.scalar_one_or_none = AsyncMock(return_value=None)
    mock_execute_result.scalar = AsyncMock(return_value=None)
    mock_execute_result.first = AsyncMock(return_value=None)
    mock_execute_result.all = AsyncMock(return_value=[])
    
    mock.execute.return_value = mock_execute_result
    
    return mock


@pytest.fixture
def client(mock_db):
    
    def override_get_db():
        return mock_db
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_device_data():
    return {
        'name': 'sensor',
        'type': 'teapot',
    }

@pytest.fixture
def sample_wrong_device_data():
    return {
        "name": "Test Device",
        "type": "skibidi",
    }

@pytest.fixture
def sample_scenario_data():
    return {
        'name': 'my',
        'trigger': {
            'trigger_type': 'none'
        },
        'actions': [
            {
                'action_type': 'switch',
                'device_id': 'ece32d56-1be1-43e8-8ead-1641a588ca9b',
                'mode': 'on'
            }
        ]
    }



@pytest.fixture
def auth_headers():
    """Фикстура для заголовков аутентификации (если нужно)"""
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def benchmark_config():
    """Конфигурация для benchmark тестов"""
    return {
        "min_time": 0.01,
        "max_time": 1.0,
        "min_rounds": 5,
        "warmup": True,
    }

@pytest.fixture(autouse=True)
def clear_caches():
    """Очищает возможные кэши между тестами"""
    import gc
    gc.collect()
    yield
    gc.collect()

# @pytest.fixture
# def sample_scenario_data():
#     return {
#         "name": "Test Scenario",
#         "description": "Test Description",
#         "script_code": "print('Hello World')"
#     }