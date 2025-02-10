import sqlite3
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
base = sqlite3.connect('reviewers.db')
cursor = base.cursor()

class id(StatesGroup):
    id_in_bd = State()

def create_tables():
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

async def register_check_sec_register(id_tg):
    cursor.execute("SELECT id_tg FROM Users WHERE id_tg = ?", (id_tg,))
    id_tg_in_bd = cursor.fetchone()
    if id_tg_in_bd == None:
        id_tg_in_bd = 0
        return id_tg_in_bd
    else:
        id_tg_in_bd = id_tg_in_bd[0]
        return id_tg_in_bd

async def add_user(id_tg, gitlab, username, first_name, last_name, teamlead):
    cursor.execute(
        'INSERT INTO Users (id_tg, gitlab, username, first_name, last_name, is_teamlead) VALUES  (?, ?, ?, ?, ?, ?)',
        (id_tg, gitlab, username, first_name, last_name, teamlead))

async def del_account(id_tg):
    cursor.execute("DELETE from Users where id_tg = ?", (id_tg,))

async def gitlab_select_where_id_tg_equal(id_tg):
    cursor.execute("SELECT gitlab FROM Users WHERE id_tg = ?", (id_tg, ))
    gitlab = cursor.fetchone()
    return gitlab

async def chek_second_set_reviewer_chek_author(author):
    cursor.execute("SELECT reviewers FROM reviewers WHERE author = ?", (author,))
    select = cursor.fetchone()
    return select

async def set_reviewer(author, reviewer):
    cursor.execute('INSERT INTO reviewers (author, reviewers) VALUES  (?, ?)', (author, reviewer,))

async def unset_reviewer(author, reviewers):
    cursor.execute(('DELETE FROM reviewers WHERE author = ? AND reviewers = ?'), [author, reviewers])


