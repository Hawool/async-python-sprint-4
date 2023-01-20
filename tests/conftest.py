from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from src.main import app


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client
