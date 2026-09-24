import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import engine, session_scope
from database.models import Base, User
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

    async def update(self, telegram_id, user_update: UserUpdate):
        # Получаем только переданные поля (исключаем None)
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            return None
        user = await self._get_user_by_telegram_id(telegram_id)
        if user is None:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return UserResponse.model_validate(user)

    async def get_user_by_telegram_id(self, telegram_id: int):
        user = await self._get_user_by_telegram_id(telegram_id)
        if user is None:
            return None
        return UserResponse.model_validate(user)

    async def get_all_users(self):
        query = select(User)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

    async def _get_user_by_telegram_id(self, telegram_id: int)->User:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        return user

async def main():
    async with session_scope() as session:
        user = UserService(session)
        all_users = await user.get_all_users()
        print(len(all_users))
        for user in all_users:
            print(f"{user.telegram_id} free_plan:{user.free_plan} start_plan:{user.start_plan}\n")

async def update_user_with_fields(telegram_id: int, data: UserUpdate):
    async with session_scope() as session:
        service = UserService(session)
        user = await service.update(telegram_id, data)
        return UserResponse.model_validate(user)


if __name__ == '__main__':
    # asyncio.run(make_user_payed(6305024563))
    data = {
        'free_plan': False,
        'start_plan': datetime(2020, 1, 1),
    }
    new_data = UserUpdate(**data)
    # asyncio.run(main())
    res = asyncio.run(update_user_with_fields(telegram_id=470946767, data=new_data))
    print(res)


