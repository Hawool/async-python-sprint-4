import asyncio
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, AsyncConnection, AsyncTransaction
from sqlalchemy.orm import sessionmaker

from src.core.config import app_settings
from src.db.db import Base, get_session
from src.main import app
from tests.db_utils import create_db

app_settings.DATABASE_DSN = f'{app_settings.DATABASE_DSN}_test'

engine = create_async_engine(f'{app_settings.DATABASE_DSN}', echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
async def get_test_session() -> AsyncSession:
    async with async_session() as session:
        yield session
app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(scope='session')
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def _create_db() -> None:
    await create_db(url=app_settings.DATABASE_DSN, base=Base)


@pytest_asyncio.fixture()
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(app_settings.DATABASE_DSN, echo=True, future=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
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



#######################################################################################################
# engine = create_async_engine(f'{app_settings.DATABASE_DSN}_test', echo=True, future=True)
# async_session = sessionmaker(
#     engine, class_=AsyncSession, expire_on_commit=False
# )
#
#
# async def get_test_session() -> AsyncSession:
#     async with async_session() as session:
#         yield session
#
#
# app.dependency_overrides[get_session] = get_test_session
#
#
# @pytest_asyncio.fixture()
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url='http://test') as client:
#         yield client
#
#
# @pytest_asyncio.fixture()
# async def base():
#     """
#     creates DB test_collector,
#     creates tables,
#     allows to make queries,
#     when test is done, drops DB
#     """
#     if not database_exists(engine.url):
#         create_async_engine(engine.url)
#
#     with engine.connect() as conn:
#         # add uuid_generate_v4() extension
#         conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
#
#     Base.metadata.create_all(bind=engine)
#     with async_session as db:
#         yield db
#
#     if database_exists(engine.url):
#         drop_database(engine.url)
