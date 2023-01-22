import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                    AsyncTransaction, create_async_engine)
from sqlalchemy.orm import sessionmaker

from src.core.config import app_settings
from src.db.db import Base, get_session
from src.main import app
from src.models.urls import UrlModel
from tests.db_utils import create_db, DBUtils

app_settings.DATABASE_DSN = f'{app_settings.DATABASE_DSN}_test'


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def _create_db() -> None:
    await create_db(url=app_settings.DATABASE_DSN, base=Base)


@pytest_asyncio.fixture(scope='session')
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(app_settings.DATABASE_DSN, echo=True, future=True)
    try:
        yield engine
    finally:
        # await engine.dispose()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope='session')
async def db_connection(engine: AsyncEngine) -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(autouse=True)
async def db_transaction(db_connection: AsyncConnection) -> AsyncGenerator[AsyncTransaction, None]:
    """
    Recipe for using transaction rollback in tests
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites  # noqa
    """
    async with db_connection.begin() as transaction:
        yield transaction
        await transaction.rollback()


@pytest_asyncio.fixture(autouse=True)
async def session_f(db_connection: AsyncConnection, monkeypatch: MonkeyPatch) -> AsyncGenerator[AsyncSession, None]:
    session_maker = sessionmaker(db_connection, class_=AsyncSession, expire_on_commit=False)
    monkeypatch.setattr('src.db.db.async_session', session_maker)

    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client


@pytest_asyncio.fixture()
async def test_url(session_f: AsyncSession):
    url = UrlModel(
        url='http://google.com',
        name='google'
    )
    session_f.add(url)
    await session_f.commit()
