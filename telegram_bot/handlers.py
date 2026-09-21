import aiohttp
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import Message

from hiddify.request import add_period
from telegram_bot.message_templates import instruction_message

import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} start bot")
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
async def info(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"Инструкция")
    await message.answer(instruction_message)

@router.message(F.text.lower() == "подключить устройство")
async def add_device(message: Message, ext_session: aiohttp.client.ClientSession):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Подключение устройства")
    user_name = message.from_user.full_name
    logger.debug(f"user_id::{user_id}, user_name::{user_name}")
    await add_period(
        user_name=user_name,
        telegram_id=user_id,
        session=ext_session,
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
    await message.reply("пожелания")
