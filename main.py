import asyncio

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import logging

from dotenv import load_dotenv
import os

from telegram_bot.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

token = os.getenv("TELEGRAM_TOKEN")
proxy_server = os.getenv("PROXY_SERVER")
IP = os.getenv("RUS_IP")

dp = Dispatcher()

async def main():
    async with aiohttp.ClientSession() as ext_session:
        try:
            dp["ext_session"] = ext_session
            dp.include_router(router)
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await bot.session.close()

async def check_ip(ip):
    url = "https://ifconfig.me/"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.text()
            return ip in response


if __name__ == '__main__':
    session = None
    if asyncio.run(check_ip(IP)):
        proxy_session = AiohttpSession(proxy=proxy_server)
        session = proxy_session
    bot = Bot(
        token=token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    asyncio.run(main())
