import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import sqlite3
import environ
import re
import random
import time
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sys
import config
import re
import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.markdown import hlink
from config import Config
from aiogram.types import (
    CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message,
)
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import Window
from aiogram import Bot, Dispatcher, executor, types # Импортирование необходимых библиотек
import logging
import keys as kb


env = environ.Env()
environ.Env.read_env()
TEAMLEAD = env('TEAMLEAD')
#print(TEAMLEAD)
token = env('token')

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Кнопочки', reply_markup=kb.keyboardBtns)

# Хендлер для обычной клавиатуры
@dp.message_handler(text=['Один'])
async def keyboardFunc(message: types.Message):
    if message.text == 'Один':
        await message.answer('Кнопка "Один" нажата :)')

@dp.message_handler(text=['Два'])
async def keyboardFunc(message: types.Message):
    if message.text == 'Два':
        await message.answer('Кнопка "Два" нажата :)')



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())