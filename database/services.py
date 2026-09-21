from database.models import Base
from database.db import engine


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)




