from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from database.models import Base
from database.db import engine, session_scope
from database.models import User
from database.schemas import UserCreate, UserResponse, UserUpdate


async def create_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)



class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: UserCreate):
        new_user = User(telegram_id=user.telegram_id)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserResponse.model_validate(new_user)

    async def update(self, user: UserUpdate):
        pass

    async def get_user_by_telegram_id(self, telegram_id: int):
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return UserResponse.model_validate(user)

    async def get_all_users(self):
        query = select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

async def main():
    async with session_scope() as session:
        user = UserService(session)
        all_users = await user.get_all_users()
        print(all_users)

if __name__ == '__main__':
    asyncio.run(main())


