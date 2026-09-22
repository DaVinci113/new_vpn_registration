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
        new_user = User(
            telegram_id=user.telegram_id,
            end_plan=user.end_plan,
        )
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
        if user is None:
            return None
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

async def make_user_payed(user_id: int):
    async with session_scope() as session:
        user = select(User).where(User.telegram_id == user_id)
        db_user = await session.execute(user)
        change_user = db_user.scalar_one_or_none()
        change_user.free_plan = False
        print(f"{change_user.telegram_id}\n"
              f"{change_user.free_plan}\n"
              f"{change_user.end_plan}")
        await session.commit()
        await session.refresh(change_user)


if __name__ == '__main__':
    asyncio.run(make_user_payed(6305024563))
    # asyncio.run(main())


