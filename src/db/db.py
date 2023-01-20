from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

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
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
