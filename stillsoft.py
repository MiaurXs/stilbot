import asyncio
import logging
import sqlite3
import environ
import re
import random
import time
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
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
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import Window
import keys as kb
from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
import datetime
from datetime import date
from sqlalchemy import create_engine


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
reviewers TEXT NOT NULL,
leave_start TEXT,
leave_end TEXT
)
''')


env = environ.Env()
environ.Env.read_env()
TEAMLEAD = env('TEAMLEAD')
token = env('token')


logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())


i = 0
teamlead = 0


class UserState(StatesGroup):
    gitlab = State()

class State_leave(StatesGroup):
    gitlab = State()
    date_start = State()
    date_end = State()

class Set_rev(StatesGroup):
    set_author = State()
    set_reviewer = State()

class Unset_rev(StatesGroup):
    unset_reviewer = State()
    unset_author = State()

class Quit(StatesGroup):
    quit = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет,\nвыберите нужный вам пункт\n/m - кнопки', reply_markup=kb.keyboardBtns)


@dp.message_handler(commands=["m"])
async def menu(message: types.Message):
    await message.answer('Кнопки ', reply_markup=kb.keyboardBtns)


@dp.message_handler(text=["Регистрация"])
async def try_reg_and_names(message: types.Message):
    if message.text == 'Регистрация':
        base = sqlite3.connect('reviewers.db')
        cursor = base.cursor()
        id_tg = message.from_user.id # id в тг

        cursor.execute("SELECT id_tg FROM Users WHERE id_tg = ?", (id_tg,))
        id_tg_in_bd = cursor.fetchone() #id в базе данных
        if id_tg_in_bd == None:
            id_tg_in_bd = 0
        else:
            id_tg_in_bd = id_tg_in_bd[0]

        if str(id_tg) == str(id_tg_in_bd): #совпадение id в тг и базе данных
            await bot.send_message(id_tg, "Вы уже зарегистрированы")
        else:
            await message.answer(f"Ваше имя в gitlab: ")
            await UserState.gitlab.set()

@dp.message_handler(state=UserState.gitlab)
async def get_gitlab_username(message: types.Message, state: FSMContext):
    await state.update_data(gitlab=message.text)
    gitlab = await state.get_data()
    gitlab = gitlab['gitlab']
    id_tg = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if last_name == None:
        last_name = 'None'

    if gitlab == TEAMLEAD:
        teamlead = 1
    else:
        teamlead = 0
    if teamlead == 1:
        await bot.send_message(id_tg, 'Вы teamlead')
    elif teamlead == 0:
        await bot.send_message(id_tg, 'Ждите пока вас назначат reviewer(ом)')
    else:
        await bot.send_message(id_tg, 'Ошибка записи значения "teamlead"')

    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute(
        'INSERT INTO Users (id_tg, gitlab, username, first_name, last_name, is_teamlead) VALUES  (?, ?, ?, ?, ?, ?)',
        (id_tg, gitlab, username, first_name, last_name, teamlead))
    base.commit()

    await bot.send_message(id_tg, "Вы зарегистрированы", reply_markup=kb.keyboardBtns)

    await state.finish()


@dp.message_handler(text=["Удалить учётную запись"])
async def account_del(message: types.Message):
    if message.text == 'Удалить учётную запись':
        id_tg = message.from_user.id

        base = sqlite3.connect('reviewers.db')
        cursor = base.cursor()
        cursor.execute("DELETE from Users where id_tg = ?", (id_tg,))
        base.commit()
        await bot.send_message(id_tg, "Учетная запись удалена")

@dp.message_handler(text=["Назначить reviewer(a) - доступно только teamlead(у)"])
async def set_author(message: types.Message):
    if message.text == 'Назначить reviewer(a) - доступно только teamlead(у)':
        id_tg = message.from_user.id

        base = sqlite3.connect('reviewers.db')
        cursor = base.cursor()
        cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg, ))
        gitlab = cursor.fetchone()
        if gitlab == None:
            await bot.send_message(id_tg,
                                   'вы не зарегестрированы, для регестрации нажмите на кнопку "зарегестрироваться"')
        else:
            gitlab = gitlab[0]

            if gitlab == TEAMLEAD:
                teamlead = 1
            else:
                teamlead = 0

            if teamlead == 1:
                author = await message.answer("Кому? (gitlab)")
                await Set_rev.set_author.set()
            else:
                await bot.send_message(id_tg, "Этой командой может пользоваться только teamlead")

@dp.message_handler(state=Set_rev.set_author)
async def set_reviewer(message: types.Message, state: FSMContext):
    await state.update_data(set_author=message.text)
    data = await state.get_data()
    author = data['set_author']

    reviewers = await message.answer("Кого? (gitlab)")
    await Set_rev.set_reviewer.set()

@dp.message_handler(state=Set_rev.set_reviewer)
async def set_rev_finish(message: types.Message, state: FSMContext):
    await state.update_data(set_reviewer=message.text)
    data = await state.get_data()
    reviewer = data['set_reviewer']
    author = data['set_author']
    id_tg = message.from_user.id

    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("SELECT reviewers FROM reviewers WHERE author = ?", (author,))
    check_reviewer = cursor.fetchone()
    if check_reviewer == None:
        check_reviewer = None
    else:
        check_reviewer = check_reviewer[0]

    if check_reviewer != None:
        await bot.send_message(id_tg, f'этот reviewer уже есть у {author}, нельзя назначить 2ой раз', reply_markup=kb.keyboardBtns)
        await state.finish()
    else:
        cursor.execute('INSERT INTO reviewers (author, reviewers) VALUES  (?, ?)', (author, reviewer,))
        base.commit()

        await bot.send_message(id_tg, "Reviewer успешно назначен", reply_markup=kb.keyboardBtns)
        await state.finish()


@dp.message_handler(text=["Снять reviewer(a) - доступно только teamlead(у)"])
async def unset_rev_unset_author(message: types.Message):
    if message.text == 'Снять reviewer(a) - доступно только teamlead(у)':
        id_tg = message.from_user.id

        base = sqlite3.connect('reviewers.db')
        cursor = base.cursor()

        cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg,))
        gitlab = cursor.fetchone()

        if gitlab == None:
            await bot.send_message(id_tg,
                                   'вы не зарегестрированы, для регестрации нажмите на кнопку "зарегестрироваться"')
        else:
            gitlab = gitlab[0]

            if gitlab == TEAMLEAD:
                teamlead = 1
            else:
                teamlead = 0

            if teamlead == 1:
                author = await message.answer("Кому? (gitlab)")

                await Unset_rev.unset_author.set()

            else:
                await bot.send_message(id_tg, "Этой командой может пользоваться только teamlead", reply_markup=kb.keyboardBtns)

@dp.message_handler(state=Unset_rev.unset_author)
async def unset_reviewer_answer(message: types.Message, state: FSMContext):
    await state.update_data(unset_author=message.text)
    id_tg = message.from_user.id
    data = await state.get_data()

    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()

    cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg,))
    gitlab = cursor.fetchone()
    gitlab = gitlab[0]

    if gitlab == TEAMLEAD:
        teamlead = 1
    else:
        teamlead = 0

    await message.answer("Кого? (gitlab)")

    await Unset_rev.unset_reviewer.set()

@dp.message_handler(state=Unset_rev.unset_reviewer)
async def unset_reviewer(message: types.Message, state: FSMContext):
    await state.update_data(unset_reviewer=message.text)
    id_tg = message.from_user.id
    data = await state.get_data()

    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    author = data['unset_author']
    reviewers = data['unset_reviewer']

    cursor.execute(('DELETE FROM reviewers WHERE author = ? AND reviewers = ?'), [author, reviewers])

    base.commit()

    await bot.send_message(id_tg, "Reviewer снят", reply_markup=kb.keyboardBtns)

    await state.finish()


base.close()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
