from datetime import datetime, timedelta

import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message

from database.schemas import UserCreate
from database.services import UserService
from hiddify.request import add_device, check_user_device
from telegram_bot.message_templates import instruction_message, wishes_message

from hiddify.config import plan

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, user_repo: UserService):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} start bot")
    current_date = datetime.now()
    if user:= await user_repo.get_user_by_telegram_id(user_id):
        user_name = message.from_user.username
        await message.reply(f"С возвращением {user_name}")
        return
    else:
        new_user = UserCreate(
        telegram_id=user_id,
        end_plan=current_date+timedelta(days=30),
        )
        await user_repo.create(new_user)
    kb = [
        [types.KeyboardButton(text="ИНФО")],
        [types.KeyboardButton(text="Инструкция")],
        [types.KeyboardButton(text="Подключить устройство")],
        [types.KeyboardButton(text="Подписка")],
        [types.KeyboardButton(text="Пожелания")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer("Выберете пункт в меню", reply_markup=keyboard)

@router.message(F.text.lower() == "инфо")
async def info(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"инфо")
    await  message.reply("инфо")

@router.message(F.text.lower() == "инструкция")
async def instruction(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"Инструкция")
    await message.answer(instruction_message)

@router.message(F.text.lower() == "подключить устройство")
async def add_device_to_user(message: Message, user_repo: UserService):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Подключение устройства")
    user_name = message.from_user.full_name
    logger.debug(f"user_id::{user_id}, user_name::{user_name}")
    user_data = await user_repo.get_user_by_telegram_id(user_id)
    if user_data is None:
        await message.reply("Нажмите start")
        return
    if user_data.free_plan:
        volume = plan["trial"]["volume"]
        devices_count = plan["trial"]["devices"]
    else:
        volume = plan["plan"]["volume"]
        devices_count = plan["plan"]["devices"]
    user_devices = await check_user_device(user_id)
    if user_devices >= devices_count:
        await message.reply("К сожалению Вы не можете подключить больше устройств(((")
        if user_data.free_plan:
            await message.reply("Можете оплатить подписку и у Вас появится возможность подключить еще 3 устройства. И безлимит")
        return
    await add_device(
        user_name=user_name,
        telegram_id=user_id,
        duration=30,
        volume=volume,
    )
    await message.reply("подключить устройство")


@router.message(F.text.lower() == "подписка")
async def subscribe(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"оплатить")
    await  message.reply("Ваш ID для указания при оплате:\n"
                         f"{user_id}")


@router.message(F.text.lower() == "пожелания")
async def wishes(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Пожелания")
    await message.reply(wishes_message)
