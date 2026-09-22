from datetime import datetime, timedelta

import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message

from database.schemas import UserCreate
from database.services import UserService
from hiddify.request import add_device
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
    new_user = UserCreate(
        telegram_id=user_id,
        end_free_plan=current_date+timedelta(days=30),
    )
    await user_repo.create(new_user)
    kb = [
        [types.KeyboardButton(text="ИНФО")],
        [types.KeyboardButton(text="Инструкция")],
        [types.KeyboardButton(text="Подключить устройство")],
        [types.KeyboardButton(text="Подписка")],
        [types.KeyboardButton(text="Пожелания")],
        [types.KeyboardButton(text="all_users")],
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
async def info(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"Инструкция")
    await message.answer(instruction_message)

@router.message(F.text.lower() == "подключить устройство")
async def add_device_to_user(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Подключение устройства")
    user_name = message.from_user.full_name
    logger.debug(f"user_id::{user_id}, user_name::{user_name}")

    user_plan = plan["trial"]

    await add_device(
        user_name=user_name,
        telegram_id=user_id,
        duration=30,
        volume=user_plan["volume"],
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

@router.message(F.text.lower() == "all_users")
async def wishes(message: Message, user_repo=UserService):
    all_users = await user_repo.get_all_users()
    await message.reply(all_users)
