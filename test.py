import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import sqlite3
import environ
import re
import random
import time

base = sqlite3.connect('reviewers.db')
cursor = base.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
id_tg INTEGER,
gitlab TEXT NOT NULL,
username TEXT NOT NULL,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
is_teamlead INTEGER
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS reviewers (
author TEXT NOT NULL,
reviewers TEXT NOT NULL
)
''')

env = environ.Env()
environ.Env.read_env()
TEAMLEAD = env('TEAMLEAD')
print(TEAMLEAD)
token = env('token')

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
bot = Bot(token=token)

@dp.message(Command("start"))
async def start(message: types.Message):
    id_tg = message.from_user.id
    await bot.send_message(id_tg, "message_text")
    await message.answer('Привет ✌️\nнажми сюда  >>>  /reg\n/help - все команды')



@dp.message(Command("reg"))
async def reg(message: types.Message):
    global gitlab
    gitlab = await message.answer('Ваше имя в gitlab: ')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

