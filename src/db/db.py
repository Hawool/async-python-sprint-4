from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import app_settings

# Создаём базовый класс для будущих моделей
Base = declarative_base()


# Создаём движок
# Настройки подключения к БД передаём из переменных окружения, которые заранее загружены в файл настроек
engine = create_async_engine(app_settings.DATABASE_DSN, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncGenerator:
    async with async_session() as session:
        yield session
