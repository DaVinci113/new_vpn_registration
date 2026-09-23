from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.db import session_scope
from database.services import UserService


class DatabaseMiddleware(BaseMiddleware):
    """Middleware для инъекции сессии БД и репозиториев в хендлеры."""

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        # session_scope сам обработает commit при успехе и rollback при ошибке
        async with session_scope() as session:
            # Инжектируем сессию и готовый репозиторий в kwargs хендлера
            data["session"] = session
            data["user_repo"] = UserService(session)

            # Передаем управление следующему хендлеру
            return await handler(event, data)