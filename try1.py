import sqlite3
import telebot
import os
from telebot import types

# подключение бота
bot = telebot.TeleBot('5589060793:AAEvkZKe9PqfXaJDk0BTqHt8jrK92XwZ5pQ')
# проверка если нет файла БД + создание файла БД
if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("""
    CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    fname TEXT,
    lname TEXT,
    id TEXT
    );
    """)
    conn.commit()
    conn.close()


# интерфейс бота
@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup(row_width=1)
    show_db = types.InlineKeyboardButton(text='Вывести всю базу данных', callback_data='show_db')
    add_record = types.InlineKeyboardButton(text='Добавить запись', callback_data='add_record')
    del_record = types.InlineKeyboardButton(text='Удалить запись', callback_data='del_record')
    kb.add(show_db, add_record, del_record)
    bot.send_message(message.chat.id, 'Давай поработаем с базой данных. Что хочешь сделать?', reply_markup=kb)


# вывести всю базу данных
@bot.callback_query_handler(func=lambda callback: callback.data == 'show_db')
def show_db(callback):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT * FROM users")
    db_data = curs.fetchall()
    conn.close()
    if not db_data:
        bot.send_message(callback.message.chat.id, text='База данных пока пуста')
    else:
        db_message = ''
        user_count = 1
        for item in db_data:
            item = list(item)
            if None in item:
                item.remove(None)
            item = ' | '.join(item)
            db_message += f'{user_count}. @{item}\n'
            user_count += 1
            bot.send_message(callback.message.chat.id, text=db_message)


# записывает данные пользователя в БД заранее проверяя есть ли он в БД
@bot.callback_query_handler(func=lambda callback: callback.data == 'add_record')
def add_record(callback):
    user_data = (callback.from_user.username, callback.from_user.first_name, callback.from_user.last_name,
                 callback.from_user.id)
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    # Проверка через SELECT
    curs.execute(f"SELECT username FROM users WHERE username = '{callback.from_user.username}'")
    # Если уже есть в БД
    if curs.fetchall():
        bot.send_message(callback.message.chat.id, text='Ты уже был записан. Посмотри БД')
    # Если нет в БД
    elif not curs.fetchall():
        curs.execute("""
        INSERT INTO users(username, fname, lname, id)
        VALUES(?, ?, ?, ?);
        """, user_data)
        conn.commit()
        conn.close()
        bot.send_message(callback.message.chat.id, text='Добавил твою запись')


# удаление из БД записи
# запрос никнейма
@bot.callback_query_handler(func=lambda callback: callback.data == 'del_record')
def del_record_quest(callback):
    conn = sqlite3.connect('database.db')
    curs = conn.cursor()
    curs.execute("SELECT username FROM users")
    user_list = curs.fetchall()
    bot.send_message(callback.message.chat.id, 'Введите username без "@". Чтобы удалить этого человека из БД.')

    # проверка ввода и удаление записи
    @bot.message_handler(content_types=['text'])
    def del_record(message):
        if message.text in f'@{user_list}':
            bot.send_message(message.chat.id, 'Готово, удалил')
            curs.execute(f"DELETE FROM users WHERE username = '{message.text}';")
            conn.commit()
            conn.close()
        else:
            bot.send_message(message.chat.id, 'Такого пользователя нет. Или вы ввели неправильный формат.\nВведите '
                                              'username без "@".')


bot.polling()
