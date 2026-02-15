from types import SimpleNamespace
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.dependencies.http import get_current_user
from app.main import app
from app.services import Services

API_V1_PREFIX = "/api/v1"


@pytest.fixture
async def api_client(seeded_db: Dict[str, Any]) -> AsyncGenerator[AsyncClient, None]:
    """Залогиненный user1 для /api/v1/..."""
    app.dependency_overrides[get_current_user] = lambda: seeded_db["user1"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{API_V1_PREFIX}",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def api_superuser_client(seeded_db: Dict[str, Any]) -> AsyncGenerator[AsyncClient, None]:
    """Залогиненный admin для /api/v1/..."""
    app.dependency_overrides[get_current_user] = lambda: seeded_db["admin"]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{API_V1_PREFIX}",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def api_anon_client() -> AsyncGenerator[AsyncClient, None]:
    """Анонимный клиент для /api/v1/..."""
    app.dependency_overrides.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://test{API_V1_PREFIX}",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_rabbitmq():
    original = Services.rabbitmq
    Services.rabbitmq = SimpleNamespace(
        request=AsyncMock(return_value=None),
        publish=AsyncMock(return_value=True),
    )
    yield
    Services.rabbitmq = original

from dev.fixtures.db import clean_db, started_db  # noqa: F401,E402
from dev.fixtures.add_test_data import seeded_db  # noqa: F401,E402
