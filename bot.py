#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os

from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import models

import pandas as pd
import sqlite3


# Enable database
engine = create_engine('sqlite:////root/telegram_bot/bot.db', echo=True)
models.Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

EMOTIONS_2, EMOTIONS, ENERGY, ENERGY_2, ATTENTION, ATTENTION_2, CONSCIENTIOUSNESS, CONSCIENTIOUSNESS_2, PLANNING, PLANNING_2, STRESS, STRESS_2, REGIME, REGIME_2, BODY, BODY_2, READING, READING_2, COMMENT, RATING = range(20)


entry_reply_keyboard = [['/start_session', '/report', '/help']]
entry_markup = ReplyKeyboardMarkup(entry_reply_keyboard, one_time_keyboard=True, resize_keyboard=True)


def start(update, context):
    update.message.reply_text('''Это бот для отслеживания продуктивных состояний психики.''', reply_markup=entry_markup)
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text('''Бот позволяет вести ежедневник, в котором отслеживаются следующие проявления психической жизни:
1. Эмоции
2. Энергия
3. Внимание
4. Сознательность
5. Планирование
6. Стресс
7. Режим дня
8. Здоровье тела

Нажмите /start_session и бот опросит вас по этим пунктам.
Дайте оценку дня числом 0, 1 или 2, где:
0 -- продуктивность ниже нормы, проявлялись плохие привычки и состояния
1 -- продуктивность дня нормальная, незначительные проявления непродуктивных привычек и состояний
2 -- продуктивность дня высокая, проявлялось желаемое продуктивное поведение, воспитываются хорошие привычки.

Для того, чтобы получить отчет по вашим записям, нажмите /report.''', reply_markup=entry_markup)
    return ConversationHandler.END


def generate_report(update, context):
    # Read sqlite query results into a pandas DataFrame
    user = update.message.from_user
    con = sqlite3.connect("bot.db")
    df = pd.read_sql_query('''SELECT
    datetime,
    emotions,
    energy,
    attention,
    conscientiousness,
    planning,
    stress,
    regime,
    body,
    reading,
    comment,
    rating
    FROM records WHERE user_name='%s' ''' % user['username'], con)
    df.to_excel('report.xlsx', index=None, header=True)
    con.close()
    context.bot.send_document(chat_id=update.message.chat_id, document=open('report.xlsx', 'rb'))
    update.message.reply_text('''Вот ваш отчет''', reply_markup=entry_markup)
    return ConversationHandler.END


cancel_cmd = '/cancel'
reply_kb = {
    'emotions': [['Радость, удовольствие от работы'], ['Спокойная работа'], ['Тревожность, мысли мешают работать'], [cancel_cmd]],
    'enegry': [],
}


message = {
    'emotions': '''*Эмоциональное состояние:*
Опишите как ваше эмоциональное состояние влияло на вашу продуктивность.'''
}


def markup(topic):
    return ReplyKeyboardMarkup(reply_kb[topic], one_time_keyboard=True, resize_keyboard=True)


def start_session(update, context):
    update.message.reply_text(message['emotions'], reply_markup=markup('emotions'))
    return EMOTIONS


def emotions(update, context):
    msg = update.message.text
    context.user_data['emotions'] = msg
    reply = reply_kb['emotions']
    if msg == reply[0][0]:
        text = 'В чем была причина?'
    elif msg == reply[1][0]:
        text = 'Что можно сделать лучше?'
    elif msg == reply[2][0]:
        text = 'В чем причина?\nКак это можно исправить?'
    else:
        text = 'В чем причина?\nЧто можно сделать лучше?'
    update.message.reply_text(text)
    return EMOTIONS_2


sep = ': '


def emotions_2(update, context):
    context.user_data['emotions'] += sep + update.message.text

    reply_keyboard = [['Активная работа в нужном русле'], ['Работал нормально, без торможения'], ['Что-то блокирует. Работается хуже чем обычно'], ['Слабая энергия, вялость, работать тяжело'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Энергичность:*
Опишите сколько у вас сегодня энергии.''', reply_markup=markup)
    return ENERGY


def energy(update, context):
    context.user_data['energy'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return ENERGY_2


def energy_2(update, context):
    context.user_data['energy'] += sep + update.message.text

    reply_keyboard = [['Работал в потоке'], ['Хорошее, скачков нет'], ['Нормальное, внимание сбивается лишь иногда'], ['Сбивчивое, работать трудно'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Внимание:*
 * Как хорошо получается фокусировать внимание?''', reply_markup=markup)
    return ATTENTION


def attention(update, context):
    context.user_data['attention'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return ATTENTION_2


def attention_2(update, context):
    context.user_data['attention'] += sep + update.message.text

    reply_keyboard = [['Отдаю отчет своим действиям, налажен диалог с собой'], ['Приходится перебарывать себя'], ['Автопилот, врубается обезьяна'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Осознанность:*''', reply_markup=markup)
    return CONSCIENTIOUSNESS


def conscientiousness(update, context):
    context.user_data['conscientiousness'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return CONSCIENTIOUSNESS_2


def conscientiousness_2(update, context):
    context.user_data['conscientiousness'] += sep + update.message.text

    reply_keyboard = [['Работа идет четко по плану'], ['Плана нет, но важные дела делаются, без прокрастинации'], ['Вмешивается прокрастинация, чувствуется недостаток планирования'], ['Важные дела не были сделаны или не начаты вовремя'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Планирование:*''', reply_markup=markup)
    return PLANNING


def planning(update, context):
    context.user_data['planning'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return PLANNING_2


def planning_2(update, context):
    context.user_data['planning'] += sep + update.message.text

    reply_keyboard = [  ['Спокойствие, внешние вещи не трогают'], 
                        ['Небольшое фоновое напряжение'], 
                        ['Трудные задачи, большая ответственность'], 
                        ['Напряжение при подходе к работе'], 
                        ['Сильная напряженность'], 
                        ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Стресс:', reply_markup=markup)
    return STRESS


def stress(update, context):
    context.user_data['stress'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return STRESS_2


def stress_2(update, context):
    context.user_data['stress'] += sep + update.message.text

    reply_keyboard = [  ['Распорядок дня соблюдается'], 
                        ['Были нарушения распорядка'], 
                        ['/cancel']
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Режим:*
Опишите как у вас получается соблюдать режим труда, отдыха, питания и упражнений.
Недостаточный или нерегулярный отдых может снижать продуктивность.
    ''', reply_markup=markup)
    return REGIME


def regime(update, context):
    context.user_data['regime'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return REGIME_2


def regime_2(update, context):
    context.user_data['regime'] += sep + update.message.text

    reply_keyboard = [['Сон и самочувствие в норме'], ['Качество сна или самочувствие влияют на продуктивность'], ['Не могу работать из-за плохого самочувствия'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Тело:', reply_markup=markup)
    return BODY


def body(update, context):
    context.user_data['body'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return BODY_2


def body_2(update, context):
    context.user_data['body'] += sep + update.message.text

    reply_keyboard = [  ['Занимался по плану и конкретным целям, заметки сделаны'], 
                        ['Не занимался, но подобрал материал'], 
                        ['Не занимался'], 
                        ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Чтение/изучение:*
Важно заниматься каждый день.
Важно иметь конкретный план, иначе изученное будет забыто или вы изучите то, что не пригодится.''', reply_markup=markup)
    return READING


def reading(update, context):
    context.user_data['reading'] = update.message.text
    update.message.reply_text('''Напишите подробнее:
 * Что удалось узнать важного?
 * Был ли план перед чтением и заметки после чтения?
 * Сохранили ли заметки в Anki, чтобы повторить и не забыть?
 * Если не читали, то почему? С чем это связано? 
 * Что можно сделать лучше в следующий раз?''')
    return READING_2


def reading_2(update, context):
    context.user_data['reading'] += sep + update.message.text

    update.message.reply_text('''*Комментарий:*
Здесь можно описать, например
 * Как начался день
 * Пожелание себе на будущее
 * Мысль дня''')
    return COMMENT


def comment(update, context):
    text = update.message.text
    context.user_data['comment'] = text
    reply_keyboard = ['0','1','2',['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''Оценка:
Дайте оценку дня числом 0, 1 или 2, где:
0 -- продуктивность ниже нормы, проявлялись плохие привычки и состояния
1 -- продуктивность дня нормальная, незначительные проявления непродуктивных привычек и состояний
2 -- продуктивность дня высокая, проявлялось желаемое продуктивное поведение, воспитываются хорошие привычки.
Позже можно будет посмотреть на график.''', reply_markup=markup)
    return RATING


def rating(update, context): #final question
    text = update.message.text
    if text.isdigit() and 0 <= int(text) <= 2:
        context.user_data['rating'] = int(text)
    else:
        update.message.reply_text('Введите 0, 1 или 2')
        return RATING
    user = update.message.from_user
    d = context.user_data
    record = models.Record(
        user_id = user['id'],
        user_name = user['username'],
        datetime = datetime.now(),
        emotions = d['emotions'],
        energy = d['energy'],
        attention = d['attention'],
        conscientiousness = d['conscientiousness'],
        planning = d['planning'],
        stress = d['stress'],
        regime = d['regime'],
        body = d['body'],
        reading = d['reading'],
        comment = d['comment'],
        rating = int(d['rating'])
    )
    session.add(record)
    session.commit()
    update.message.reply_text('''Спасибо! Таблицу с данными за все дни можно скачать по команде /report''', reply_markup=entry_markup)
    context.user_data.clear()
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the session.", user.first_name)
    update.message.reply_text('Cancelled', reply_markup=entry_markup)
    context.user_data.clear()
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ.get('BOT_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[  CommandHandler('start', start), 
                        CommandHandler('start_session', start_session),
                        CommandHandler('help', help),
                        CommandHandler('report', generate_report)],

        states={
            EMOTIONS: [MessageHandler(Filters.text & ~Filters.command, emotions)],
            EMOTIONS_2: [MessageHandler(Filters.text & ~Filters.command, emotions_2)],
            ENERGY: [MessageHandler(Filters.text & ~Filters.command, energy)],
            ENERGY_2: [MessageHandler(Filters.text & ~Filters.command, energy_2)],
            ATTENTION: [MessageHandler(Filters.text & ~Filters.command, attention)],
            ATTENTION_2: [MessageHandler(Filters.text & ~Filters.command, attention_2)],
            CONSCIENTIOUSNESS: [MessageHandler(Filters.text & ~Filters.command, conscientiousness)],
            CONSCIENTIOUSNESS_2: [MessageHandler(Filters.text & ~Filters.command, conscientiousness_2)],
            PLANNING: [MessageHandler(Filters.text & ~Filters.command, planning)],
            PLANNING_2: [MessageHandler(Filters.text & ~Filters.command, planning_2)],
            STRESS: [MessageHandler(Filters.text & ~Filters.command, stress)],
            STRESS_2: [MessageHandler(Filters.text & ~Filters.command, stress_2)],
            REGIME: [MessageHandler(Filters.text & ~Filters.command, regime)],
            REGIME_2: [MessageHandler(Filters.text & ~Filters.command, regime_2)],
            BODY: [MessageHandler(Filters.text & ~Filters.command, body)],
            BODY_2: [MessageHandler(Filters.text & ~Filters.command, body_2)],
            READING: [MessageHandler(Filters.text & ~Filters.command, reading)],
            READING_2: [MessageHandler(Filters.text & ~Filters.command, reading_2)],
            COMMENT: [MessageHandler(Filters.text & ~Filters.command, comment)],
            RATING: [MessageHandler(Filters.text & ~Filters.command, rating)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
