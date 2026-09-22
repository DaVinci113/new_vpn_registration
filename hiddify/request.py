import asyncio

import aiohttp
import datetime
import os
from hiddify.config import headers
from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)
load_dotenv()

api_url = os.getenv("API_URL")
proxy_path = os.getenv("PROXY_PATH_USER")
hiddify_url = os.getenv("HIDDIFY_URL")
hiddify_add_user_url = f"https://{hiddify_url}/{proxy_path}/api/v2/admin/user/"



def payload(user_name, telegram_id, volume, duration):

    current_date = str(datetime.date.today())

    payload_period = {
        "added_by_uuid": "ME",
        "comment": None,
        "current_usage_GB": 0,
        "ed25519_private_key": "string",
        "ed25519_public_key": "string",
        "enable": True,
        "is_active": True,
        "lang": "ru",
        "last_online": None,
        "last_reset_time": None,
        "mode": "monthly",
        "name": user_name,
        "package_days": duration,
        "start_date": current_date,
        "telegram_id": telegram_id,
        "usage_limit_GB": volume,
        "uuid": None,
        "wg_pk": "string",
        "wg_psk": "string",
        "wg_pub": "string"
    }
    logger.info(f"User_id {telegram_id}, Добавление периода, GB:{volume} DAYS:{duration}"
                f"user_name:{user_name}")

    return payload_period

async def add_device(user_name: str, telegram_id: int, volume: int, duration: int) -> dict:
    """Тариф для пользователя, формирование json и его POST-запрос по API"""

    logger.info(f"User_id {telegram_id}, Добавление периода, "
                f"user_name:{user_name}")
    payload_json= payload(user_name=user_name, telegram_id=telegram_id, volume=volume, duration=duration)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(hiddify_add_user_url, json=payload_json, headers=headers) as resp:
                logger.info(f"User_id: {telegram_id}, Добавление периода, "
                            f"Response: {resp} user_name: {user_name}")
                resp = await resp.json()
    except Exception as ex:
        logger.error(f"User_id:{telegram_id}, Неудачный запрос, {ex}")
        resp = None
    connect_data = {
        "id": resp["id"],
        "uuid": resp["uuid"],
        "telegram_id": resp["telegram_id"],
    }

    return connect_data

async def all_data() -> list:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(hiddify_add_user_url, headers=headers) as response:
                result = await response.json()
                logger.info(f"всего устройств: {len(result)}")
    except Exception as ex:
        logger.error(f"Неудачный запрос, {ex}")
        result = None
    return result

async def check_user_device(telegram_id: int) -> int:
    data = await all_data()
    device_count = 0
    if len(data) > 0:
        for device in data:
            try:
                if device["telegram_id"] == telegram_id:
                    device_count += 1
            except Exception as ex:
                logger.error(f"user: {telegram_id} - ошибка {ex}")
    logger.info(f"user: {telegram_id} - {device_count} устройств")
    return device_count


if __name__ == '__main__':
    result = asyncio.run(check_user_device(6305024563))
    print(result)