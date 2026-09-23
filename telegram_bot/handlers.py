import logging
import os
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from database.schemas import UserCreate
from database.services import UserService
from hiddify.config import plan
from hiddify.request import add_device, check_user_device
from qr_code.qr_generate import Link
from telegram_bot.message_templates import (
    info_message,
    instruction_message,
    wishes_message, payment_message,
)

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = Router()
load_dotenv()

admin_id = os.getenv("ADMIN_TG_ID")


@router.message(Command("start"))
async def cmd_start(message: Message, user_repo: UserService):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} start bot")
    current_date = datetime.now()
    if await user_repo.get_user_by_telegram_id(user_id):
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
    await  message.reply(info_message)

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
        duration = plan["trial"]["duration"]
    else:
        volume = plan["plan"]["volume"]
        devices_count = plan["plan"]["devices"]
        duration = plan["plan"]["duration"]
    user_devices = await check_user_device(user_id)
    if user_devices >= devices_count:
        await message.reply("К сожалению Вы не можете подключить больше устройств(((")
        if user_data.free_plan:
            await message.reply("Можете оплатить подписку и у Вас появится возможность подключить еще 3 устройства. И безлимит")
        return
    connect_data = await add_device(
        user_name=user_name,
        telegram_id=user_id,
        duration=duration,
        volume=volume,
    )
    uuid_connect = connect_data["uuid"]
    link_generator = Link(name=user_name, user_id=user_id, uuid=uuid_connect)
    link = link_generator.generate_link()
    qr_path = link_generator.generate_qr_code()
    qr_file = FSInputFile(qr_path)
    await message.answer(link)
    await message.answer_photo(qr_file)


@router.message(F.text.lower() == "подписка")
async def subscribe(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"оплатить")
    await  message.answer("Ваш ID для указания при оплате:\n"
                         f"{user_id}")
    await message.answer(payment_message)


@router.message(F.text.lower() == "пожелания")
async def wishes(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Пожелания")
    await message.reply(wishes_message)


