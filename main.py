import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from core.middlewares.databs import DatabaseMiddleware
from database.services import create_table
from telegram_bot.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
proxy_server = os.getenv("PROXY_SERVER")
IP = os.getenv("RUS_IP")


async def check_ip(ip):
    url = "https://ifconfig.me/"
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        response = await resp.text()
        return ip in response

async def main():
    dp = Dispatcher()
    # Подключаем Middleware ко всем сообщениям (и коллбэкам, если нужно)
    # Можно сделать dp.message.middleware(...) и dp.callback_query.middleware(...)
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    session = None
    if await check_ip(IP):
        logger.debug(f"ip::{IP}")
        logger.info("Запуск через прокси")
        proxy_session = AiohttpSession(proxy=proxy_server)
        session = proxy_session
    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    async with aiohttp.ClientSession() as ext_session:
        try:
            await create_table()
            dp["ext_session"] = ext_session
            dp.include_router(router)
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
