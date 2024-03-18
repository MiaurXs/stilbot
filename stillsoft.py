import telebot
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

token = "6840173090:AAFLsLPSEOzVHAAkgeb4owi0bUyfXZbqED4"
bot = telebot.TeleBot(token)

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

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,''' Привет ✌️\nнажми сюда  >>>  /reg\n/help - все команды''')

@bot.message_handler(commands=['reg'])
def reg_message(message):
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    i = 0
    #print(message.chat.__dir__())
    gitlab = message.text
    id_tg = message.chat.id
    id_tg1 = str('(') + str(message.chat.id) + str(',)')
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    if last_name == None:
        last_name = 'None'
    cursor.execute("SELECT id_tg FROM Users WHERE id_tg = ?", (id_tg, ))
    sa = cursor.fetchone()
    if sa:
        print(id_tg1)
        print(sa)
        if str(id_tg1) == str(sa):
            #print('совпадение в id')
            i = 1
            bot.send_message(message.chat.id, "Вы уже зарегистрированы")

    if i == 1:
        pass
    else:
        bot.send_message(message.chat.id, "Ваше имя в gitlab: ")
        bot.register_next_step_handler(message, reg1_1message)


def reg1_1message(message):
    gitlab = message.text
    if gitlab == TEAMLEAD:
        teamlead = 1
    else:
        teamlead = 0
    if teamlead == 1:
        bot.send_message(message.chat.id, 'Чтобы назначить reviewer(а)\nНажмите,  /set_rev')
        bot.send_message(message.chat.id, 'Чтобы снять reviewer(а)\nНажмите,  /unset_rev')
    elif teamlead == 0:
        bot.send_message(message.chat.id, 'Ждите пока вас назначат reviewer(ом)')
    else:
        bot.send_message(message.chat.id, 'Ошибка записи значения "teamlead"')
    id_tg = message.chat.id
    id_tg1 = str('(') + str(message.chat.id) + str(',)')
    username = message.chat.username
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    if last_name == None:
        last_name = 'None'
    print('соединение')
    base = sqlite3.connect('reviewers.db')
    print('подключён')
    cursor = base.cursor()
    print('cursor подключён')
    cursor.execute('INSERT INTO Users (id_tg, gitlab, username, first_name, last_name, is_teamlead) VALUES  (?, ?, ?, ?, ?, ?)',
        (id_tg, gitlab, username, first_name, last_name, teamlead))
    base.commit()

    print(id_tg, username, first_name, last_name, gitlab)
    bot.send_message(message.chat.id, "Вы зарегистрированы")





@bot.message_handler(commands=['bd'])
def base_del(message):
    id_tg = message.chat.id
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("DELETE from Users where id_tg = ?", (id_tg, ))
    base.commit()
    bot.send_message(message.chat.id, "Учетная запись удалена")


@bot.message_handler(commands=['help'])
def commands(message):
    bot.send_message(message.chat.id, "/bd - удаление учетной записи\n/reg - регистрация учетной записи\n/start - начало работы бота\n/set_rev - назначить reviewer(a) - доступно только teamlead(у)\n/unset_rev - снять reviewer(a) - доступно только teamlead(у)")


@bot.message_handler(commands=['set_rev'])
def set_rev(message):
        id_tg = message.chat.id
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
            bot.send_message(message.chat.id, "Кому? (gitlab)")
            bot.register_next_step_handler(message, set_rev1)
        else:
            bot.send_message(message.chat.id, "Этой командой может пользоваться только teamlead")
def set_rev1(message):
    global author
    author = message.text
    bot.send_message(message.chat.id, "Кого? (gitlab)")
    bot.register_next_step_handler(message, set_rev2)

def set_rev2(message):
    reviewers = message.text
    print(author)
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("SELECT reviewers FROM reviewers WHERE author = ?", (author,))
    r = cursor.fetchone
    if r != None:
        bot.send_message(message.chat.id, f'этот reviewer уже есть у {author}, нельзя назначить 2ой раз')
    else:
        cursor.execute('INSERT INTO reviewers (author, reviewers) VALUES  (?, ?)', (author, reviewers))
        base.commit()
        bot.send_message(message.chat.id, "Reviewer успешно назначен")


@bot.message_handler(commands=['unset_rev'])
def set_rev3(message):
        id_tg = message.chat.id
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
            bot.send_message(message.chat.id, "Кому? (gitlab)")
            bot.register_next_step_handler(message, set_rev4)
        else:
            bot.send_message(message.chat.id, "Этой командой может пользоваться только teamlead")
def set_rev4(message):
    global author
    author = message.text
    bot.send_message(message.chat.id, "Кого? (gitlab)")
    bot.register_next_step_handler(message, set_rev5)

def set_rev5(message):
    reviewers = message.text
    base = sqlite3.connect('reviewers.db')
    cursor = base.cursor()
    cursor.execute("DELETE from reviewers where reviewers = ?", (reviewers, ))
    base.commit()
    bot.send_message(message.chat.id, "Reviewer успешно снят")

#while True:
    #time.sleep(300)
    #pass

base.close()
bot.infinity_polling()
