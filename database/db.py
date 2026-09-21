from contextlib import asynccontextmanager
from typing import AsyncIterator

from pydantic import with_config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

url = 'sqlite+aiosqlite:///db.sqlite'
engine = create_async_engine(url=url, future=True)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
