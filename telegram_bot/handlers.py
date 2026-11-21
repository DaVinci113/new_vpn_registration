import logging
import os
import sys
from datetime import datetime, timedelta

from aiogram import F, Router, types, Bot
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.schemas import UserCreate
from database.services import UserService
from hiddify.config import plan
from hiddify.request import add_device, check_user_device
from qr_code.qr_generate import Link
from telegram_bot.message_templates import *

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


router = Router()
load_dotenv()

admin_tg_id = os.getenv("ADMIN_TG_ID")
payment_link_family = os.getenv("PAYMENT_LINK_FAMILY")
payment_link_family_plus = os.getenv("PAYMENT_LINK_FAMILY_PLUS")

def main_menu():
    kb = [
        [types.KeyboardButton(text="ИНФО")],
        [types.KeyboardButton(text="Инструкция")],
        [types.KeyboardButton(text="Ссылки на скачивание")],
        [types.KeyboardButton(text="Подключить устройство")],
        [types.KeyboardButton(text="Подписка")],
        [types.KeyboardButton(text="Пожелания")],
    ]

    return types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберете пункт в меню",
    )

def download_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Android", callback_data="Android")
    builder.button(text="IOS", callback_data="IOS")
    builder.button(text="Windows", callback_data="Windows")
    builder.adjust(2)
    return builder.as_markup()

def payment_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Семейный", callback_data="family")
    builder.button(text="Семейный+", callback_data="family_plus")
    builder.adjust(2)
    return builder.as_markup()


@router.message(Command("start"))
async def cmd_start(message: Message, user_repo: UserService, bot: Bot):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} start bot")
    current_date = datetime.now()
    user_name = message.from_user.username
    if await user_repo.get_user_by_telegram_id(user_id):
        await message.reply(f"С возвращением {user_name}")
        return
    else:
        new_user = UserCreate(
        telegram_id=user_id,
        end_plan=current_date+timedelta(days=30),
        )
        new_user_id = new_user.telegram_id
        logger.info(f"new_user: {new_user_id} {user_name} start bot")
        await bot.send_message(
            chat_id=admin_tg_id,
            text=f"Новый пользователь {new_user_id} {user_name}"
        )
        await user_repo.create(new_user)

    await message.answer("Выберете пункт в меню", reply_markup=main_menu())

@router.message(F.text.lower() == "ссылки на скачивание")
async def show_download_links(message: Message):
    user_id = message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"ссылки на скачивание")
    await message.reply("Выберете Вашу платформу", reply_markup=download_keyboard())

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
            await message.reply("Можете оплатить подписку и у Вас появится возможность подключить еще 4 устройства. И безлимит")
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
    await message.answer_photo(qr_file, reply_markup=main_menu())

@router.callback_query(F.data == "Android")
async def android(callback: CallbackQuery):
    user_id = callback.message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"Android")
    await callback.message.answer(link_message)
    await callback.message.answer(link_android, reply_markup=main_menu())

@router.callback_query(F.data == "IOS")
async def android(callback: CallbackQuery):
    user_id = callback.message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"IOS")
    await callback.message.answer(link_message)
    await callback.message.answer(link_ios, reply_markup=main_menu())

@router.callback_query(F.data == "Windows")
async def android(callback: CallbackQuery):
    user_id = callback.message.from_user.id
    logger.info(f"User_id:{user_id} выбрал "
                f"Windows")
    await callback.message.answer(link_message)
    await callback.message.answer(link_android, reply_markup=main_menu())

@router.message(F.text.lower() == "подписка")
async def subscribe(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"оплатить")
    await  message.answer("Ваш ID для указания при оплате:\n"
                         f"{user_id}")
    await message.answer("Выберете тариф",  reply_markup=payment_keyboard())

@router.callback_query(F.data == "family")
async def subscribe_family(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"оплатить family")
    await callback.message.answer(payment_message)
    await callback.message.answer(payment_link_family)

@router.callback_query(F.data == "family_plus")
async def subscribe_family_plus(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"оплатить family_plus")
    await callback.message.answer(payment_message)
    await callback.message.answer(payment_link_family_plus)

@router.callback_query(F.data == payment_link_family or F.data == payment_link_family_plus)
async def payment_notification(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    await bot.send_message(
        chat_id=admin_tg_id,
        text=f"Пользователь {user_id} перешел по ссылке для оплаты",
    )

@router.message(F.text.lower() == "пожелания")
async def wishes(message: Message):
    user_id = message.from_user.id
    logger.info(f"User:{user_id} выбрал "
                f"Пожелания")
    await message.reply(wishes_message, reply_markup=main_menu())


