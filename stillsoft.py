import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import sqlite3
import environ
import re
import random
import time
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
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
import os
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog import Window

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
#print(TEAMLEAD)
token = env('token')

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

i = 0

#cursor.execute('SELECT id FROM Users ORDER BY RANDOM() LIMIT 1;')
#last_id = cursor.fetchone()
#if last_id == None:
#    last_id = "None"
#else:
#    last_id = last_id[0]
#last_id = None if not len(last_id) else last_id[0]
#print(last_id)

teamlead = 0

class UserState(StatesGroup):
    gitlab = State()

class Set_revi_a(StatesGroup):
    set_rev_a = State()
    set_rev_r = State()

class Unset_revi(StatesGroup):
    unset_r = State()
    unset_a = State()

class Quit(StatesGroup):
    quit = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет ✌️\nнажми сюда  >>>  /reg\n/help - все команды')

@dp.message_handler(commands=["reg"])
async def reg(message: types.Message):
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    i = 0
    id_tg = message.from_user.id
    id_tg1 = str('(') + str(id_tg) + str(',') + str(')')
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    if last_name == None:
        last_name = 'None'
    cursor.execute("SELECT id_tg FROM Users WHERE id_tg = ?", (id_tg, ))
    sa = cursor.fetchone()
    if sa:
        print(id_tg1)
        print(sa)
        if str(id_tg1) == str(sa):
            print('совпадение в id')
            i = 1
            await bot.send_message(id_tg, "Вы уже зарегистрированы")

    if i == 1:
        pass
    else:
        await message.answer(f"Ваше имя в gitlab: ")
        await UserState.gitlab.set()

@dp.message_handler(state=UserState.gitlab)
async def get_gitlab_username(message: types.Message, state: FSMContext):
    await state.update_data(gitlab=message.text)
    gitlab = await state.get_data()
    gitlab = gitlab['gitlab']
    i = 0
    id_tg = message.from_user.id
    id_tg1 = str('(') + str(id_tg) + str(',') + str(')')
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
        await bot.send_message(id_tg, 'Чтобы назначить reviewer(а)\nНажмите,  /set_rev')
        await bot.send_message(id_tg, 'Чтобы снять reviewer(а)\nНажмите,  /unset_rev')
    elif teamlead == 0:
        await bot.send_message(id_tg, 'Ждите пока вас назначат reviewer(ом)')
    else:
        await bot.send_message(id_tg, 'Ошибка записи значения "teamlead"')
    if last_name == None:
        last_name = 'None'
    print('соединение')
    base = sqlite3.connect('reviewers.db')
    print('подключён')
    cursor = base.cursor()
    print('cursor подключён')
    cursor.execute(
        'INSERT INTO Users (id_tg, gitlab, username, first_name, last_name, is_teamlead) VALUES  (?, ?, ?, ?, ?, ?)',
        (id_tg, gitlab, username, first_name, last_name, teamlead))
    base.commit()
    print(id_tg, username, first_name, last_name, gitlab)
    await bot.send_message(id_tg, "Вы зарегистрированы")
    await state.finish()





@dp.message_handler(commands=["bd"])
async def user_del(message: types.Message):
    id_tg = message.from_user.id
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("DELETE from Users where id_tg = ?", (id_tg, ))
    base.commit()
    await bot.send_message(id_tg, "Учетная запись удалена")


@dp.message_handler(commands=["help"])
async def commands(message: types.Message):
    id_tg = message.from_user.id
    await bot.send_message(id_tg, "/bd - удаление учетной записи\n/reg - регистрация учетной записи\n/start - начало работы бота\n/set_rev - назначить reviewer(a) - доступно только teamlead(у)\n/unset_rev - снять reviewer(a) - доступно только teamlead(у)\n/help - все команды")


@dp.message_handler(commands=["set_rev"])
async def set_rev_a(message: types.Message):
        id_tg = message.from_user.id
        base = sqlite3.connect('reviewers.db')
        cursor = base.cursor()
        cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg, ))
        gitlab = cursor.fetchone()
        gitlab = gitlab[0]
        print(gitlab)
        if gitlab == TEAMLEAD:
            teamlead = 1
        else:
            teamlead = 0
        if teamlead == 1:
            author = await message.answer("Кому? (gitlab)")
            await Set_revi_a.set_rev_a.set()
        else:
            await bot.send_message(id_tg, "Этой командой может пользоваться только teamlead")

@dp.message_handler(state=Set_revi_a.set_rev_a)
async def set_rev1_a(message: types.Message, state: FSMContext):
    await state.update_data(set_rev_a=message.text)
    data = await state.get_data()
    author = data['set_rev_a']
    print(author)
    reviewers = await message.answer("Кого? (gitlab)")
    await Set_revi_a.set_rev_r.set()

@dp.message_handler(state=Set_revi_a.set_rev_r)
async def set_rev_r(message: types.Message, state: FSMContext):
    await state.update_data(set_rev_r=message.text)
    data = await state.get_data()
    reviewers = data['set_rev_r']
    author = data['set_rev_a']
    print(author, reviewers)
    id_tg = message.from_user.id
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("SELECT reviewers FROM reviewers WHERE author = ?", (author,))
    r = cursor.fetchone()
    if r == None:
        r = None
    else:
        r = r[0]
    print(r)
    if r != None:
        await bot.send_message(id_tg, f'этот reviewer уже есть у {author}, нельзя назначить 2ой раз')
        await state.finish()
    else:
        cursor.execute('INSERT INTO reviewers (author, reviewers) VALUES  (?, ?)', (author, reviewers))
        base.commit()
        await bot.send_message(id_tg, "Reviewer успешно назначен")
        await state.finish()
@dp.message_handler(commands=["unset_rev"])
async def unset_rev0(message: types.Message):
    id_tg = message.from_user.id
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg, ))
    gitlab = cursor.fetchone()
    if gitlab == None:
        gitlab = None
    else:
        gitlab = gitlab[0]
    print(gitlab)
    if gitlab == TEAMLEAD:
        teamlead = 1
    else:
        teamlead = 0
    if teamlead == 1:
        author = await message.answer("Кому? (gitlab)")
        await Unset_revi.unset_a.set()
    else:
        await bot.send_message(id_tg, "Этой командой может пользоваться только teamlead")

@dp.message_handler(state=Unset_revi.unset_a)
async def unset_rev(message: types.Message, state: FSMContext):
    await state.update_data(unset_a=message.text)
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
    reviewers = await message.answer("Кого? (gitlab)")
    await Unset_revi.unset_r.set()

@dp.message_handler(state=Unset_revi.unset_r)
async def unset_rev1(message: types.Message, state: FSMContext):
    await state.update_data(unset_r=message.text)
    id_tg = message.from_user.id
    data = await state.get_data()
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    author = data['unset_a']
    print(author)
    reviewers = data['unset_r']
    print(reviewers)
    cursor.execute(('DELETE FROM reviewers WHERE author = ? AND reviewers = ?'), [author, reviewers])
    base.commit()
    await bot.send_message(id_tg, "Reviewer снят")
    await state.finish()

@dp.message_handler(state=Quit.quit)
async def quit(message: types.Message):
    pass


base.close()
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
