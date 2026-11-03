"""
Pytest fixtures and environment resets.
"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.storage.repository import repo
from app.core.frequency_capper import frequency_capper
from app.core.deduplicator import deduplicator


@pytest.fixture(autouse=True)
def reset_state():
    repo.reset()
    frequency_capper.reset()
    deduplicator.reset()
    yield


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
