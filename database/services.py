from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Base
from database.db import engine, session_scope
from database.models import User


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self,
                          telegram_id: int,
                          ):
        pass
