# coding: utf8
import sqlite3
import time
import telebot
from telebot import types
from time import sleep
from datetime import datetime, timedelta
import config
import logging
import pprint
token = '1119364128:AAHEplrr0lPkDZ_GyNtes6dbQWyQ6tNj2Tk'
import json

ADMIN = 155358934
bot = telebot.AsyncTeleBot(token=token, skip_pending=False, threaded=False, num_threads=100, parse_mode='html')
markup = types.ReplyKeyboardMarkup()
itembtna = types.KeyboardButton('/paste_text')
itembtnb = types.KeyboardButton('/stats')
itembtnc = types.KeyboardButton('/help')
itembtnd = types.KeyboardButton('/start')
ru_button = types.InlineKeyboardButton(text="Русский🇷🇺", callback_data=f"select_ru")
en_button = types.InlineKeyboardButton(text="English🇬🇧", callback_data=f"select_en")
es_button = types.InlineKeyboardButton(text="Español🇪🇸", callback_data=f"select_es")
select_lang_keyb = types.InlineKeyboardMarkup(row_width=3)
select_lang_keyb.row(es_button, en_button, ru_button)

users = {

}

start_message = \
    """
Elige un idioma
Choose a language
Выбери язык
"""

multilangmessages = {
    "start_message": {"ES": "Hola! Como podemos ayudarte? Haz su pregunta.",
                      "EN": "Hello! How can we help you? Ask your question.",
                      "RU": "Здравствуйте! Чем можем вам помочь? Задавайте ваш вопрос."},
    "for_text_message": dict(ES = "Gracias! Te responderemos en breve.", EN = "Thanks! We will answer you shortly.",
                             RU = "Спасибо! В скором времени мы вам ответим.")

}

tickets = {

}


@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in users.keys():
        if users[message.chat.id] in ["ES", "EN", "RU"]:
            bot.send_message(message.chat.id, multilangmessages["start_message"][users[message.chat.id]])
        else:
            add_new_user(message.from_user.id)
    else:
        add_new_user(message.from_user.id)


@bot.message_handler(commands=['users'])
def howusers(message):
    update_users_read()
    if message.chat.id == ADMIN:
        bot.send_message(message.chat.id, f"<em>Кол-во пользователей</em>\n\n<b>{len(users)}</b> пользователей")
    else:
        pass

def add_new_user(user_id):
    bot.send_message(user_id, start_message, reply_markup=select_lang_keyb)


@bot.message_handler(commands=['lang'])
def change_lang(message):
    add_new_user(message.from_user.id)


@bot.message_handler(func = lambda message: message.text[0] != "/")
def messages(message):
    message_id = message.chat.id
    name = message.chat.first_name
    username = message.chat.username
    message_text = message.text
    message_date = message.date
    if int(message.chat.id) == ADMIN:
        try:
            bot.send_message(message.reply_to_message.forward_from.id, message.text)
        except Exception as e:
            pass
    elif message.text != '/close':
        if message.chat.id in users.keys():
            if users[message.chat.id] in ["ES", "EN", "RU"]:
                try:
                    bot.forward_message(ADMIN, message.chat.id, message.message_id)

                    if datetime.now() < tickets[message.from_user.id] + timedelta(minutes = 1):
                        pass
                    elif datetime.now() > tickets[message.from_user.id] + timedelta(minutes = 1):
                        bot.send_message(message.chat.id, multilangmessages["for_text_message"][users[message.chat.id]])
                        tickets[message.from_user.id] = datetime.now()
                except Exception as e:
                    bot.send_message(message.chat.id, multilangmessages["for_text_message"][users[message.chat.id]])
                    tickets[message.from_user.id] = datetime.now()

            else:
                add_new_user(message.from_user.id)

        else:
            add_new_user(message.from_user.id)


@bot.callback_query_handler(lambda call: call.data in ["select_ru", "select_en", "select_es"])
def select_lang(call: types.CallbackQuery):
    if call.data == "select_ru":
        users[call.from_user.id] = "RU"
    if call.data == "select_en":
        users[call.from_user.id] = "EN"
    if call.data == "select_es":
        users[call.from_user.id] = "ES"

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=multilangmessages["start_message"][users[call.from_user.id]])
    tickets[call.message.from_user.id] = datetime.now()
    update_users_write()


def update_users_write():
    with open('users.json', 'w', encoding='UTF-8') as write_users:
        json.dump(users, write_users, ensure_ascii=False, indent=4)


def update_users_read():
    global users
    with open('users.json', 'r', encoding='UTF-8') as read_users:
        users = json.load(read_users)

    temp_dict = {}
    for key, val in users.items():
        temp_dict[int(key)] = val

    users = {}
    users = temp_dict



if __name__ == '__main__':
    update_users_read()
    bot.polling(none_stop=True)
