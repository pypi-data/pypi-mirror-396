"""Модуль, предоставляющий весь проект возможность обращаться к базе данных
Важный метод get_db"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# по параметрам обращаемся к БД
async_engine = create_async_engine(
    os.environ.get('DATABASE_URL'),
    echo=True,
    future=True
)

"""создаем сессию"""
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

"""обращение к БД"""
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()