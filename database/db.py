from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / 'database' / 'db.sqlite3'

url = f'sqlite+aiosqlite:///{DB_FILE}'
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
