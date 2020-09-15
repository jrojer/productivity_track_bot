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

EMOTIONS_2, EMOTIONS, ENERGY, ENERGY_2, ATTENTION, ATTENTION_2, CONSCIENTIOUSNESS, CONSCIENTIOUSNESS_2, PROCRASTINATION, PROCRASTINATION_2, STRESS, STRESS_2, REGIME, REGIME_2, BODY, BODY_2, COMMENT, RATING, FINISH = range(19)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{}: {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


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
5. Прокрастинация
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
    procrastination,
    stress,
    regime,
    body,
    comment,
    rating
    FROM records WHERE user_name='%s' ''' % user['username'], con)
    df.to_excel('report.xlsx', index=None, header=True)
    con.close()
    context.bot.send_document(chat_id=update.message.chat_id, document=open('report.xlsx', 'rb'))
    update.message.reply_text('''Вот ваш отчет''', reply_markup=entry_markup)
    return ConversationHandler.END


def start_session(update, context):
    reply_keyboard = [['Радость, любовь к жизни'], ['Спокойная работа'], ['Тревожность'], ['Негативные эмоции, скачки настроения'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Эмоциональное состояние:*
Опишите как ваше эмоциональное состояние влияло на вашу продуктивность.''', reply_markup=markup)
    return EMOTIONS


def emotions(update, context):
    context.user_data['emotions'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * Какие эмоции вас посещали? 
 * В чем была причина? 
 * Что можно сделать лучше?''')
    return EMOTIONS_2


sep = ': '

def emotions_2(update, context):
    context.user_data['emotions'] += sep + update.message.text

    reply_keyboard = [['Активная работа в нужном русле'], ['Нормально, без усталости'], ['Что-то блокирует'], ['Слабая энергия, вялость'], ['/cancel']]
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

    reply_keyboard = [['Важные и срочные дела делаются первыми'], ['В основном важные дела делаются, но была прокрастинация'], ['Важные дела не были сделаны или начаты вовремя'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('''*Прокрастинация:*''', reply_markup=markup)
    return PROCRASTINATION


def procrastination(update, context):
    context.user_data['procrastination'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return PROCRASTINATION_2


def procrastination_2(update, context):
    context.user_data['procrastination'] += sep + update.message.text

    reply_keyboard = [['Спокоен, внешние вещи не трогают'], ['Трудные задачи, большая ответственность'], ['Небольшое напряжение при подходе к работе'], ['Сильная напряженность'], ['/cancel']]
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

    reply_keyboard = [['Соблюдал заданный распорядок труда, отдыха, питания и упражнений'], ['Соблюдал основные правила, дурные привычки не проявлялись'], ['Нарушение порядка труда и отдыха, рецедив дурных привычек'], ['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Режим:', reply_markup=markup)
    return REGIME


def regime(update, context):
    context.user_data['regime'] = update.message.text
    update.message.reply_text('''Напишите подробнее
 * С чем это связано? 
 * Что можно сделать лучше?''')
    return REGIME_2


def regime_2(update, context):
    context.user_data['regime'] += sep + update.message.text

    reply_keyboard = [['Норма, чувствую себя хорошо, ничего не беспокоит'], ['Есть небольшие отклонения от нормы'], ['Болезнь'], ['/cancel']]
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

    update.message.reply_text('Комментарий:')
    return COMMENT


def comment(update, context):
    text = update.message.text
    context.user_data['comment'] = text
    reply_keyboard = ['0','1','2',['/cancel']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Оценка:', reply_markup=markup)
    return RATING


def rating(update, context): #final question
    text = update.message.text
    if text.isdigit() and 0 <= int(text) <= 2:
        context.user_data['rating'] = int(text)
    else:
        update.message.reply_text('Введите 0, 1 или 2')
        return RATING
    reply_keyboard = [['Save', 'Discard']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(facts_to_str(context.user_data), reply_markup=markup)
    return FINISH 


def finish(update, context):
    text = update.message.text
    if text == 'Save':
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
            procrastination = d['procrastination'],
            stress = d['stress'],
            regime = d['regime'],
            body = d['body'],
            comment = d['comment'],
            rating = int(d['rating'])
        )
        session.add(record)
        session.commit()
        reply_text = 'Saved'
    else:
        reply_text = 'Entry discarted'
    markup = ReplyKeyboardMarkup([['/start_session', '/report','/help']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)
    context.user_data.clear()
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the session.", user.first_name)
    markup = ReplyKeyboardMarkup([['/start_session', '/report', '/help']], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text('Cancelled', reply_markup=markup)
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
        entry_points=[CommandHandler('start', start), CommandHandler('start_session', start_session),CommandHandler('help', help),CommandHandler('report', generate_report)],

        states={
            EMOTIONS: [MessageHandler(Filters.text & ~Filters.command, emotions)],
            EMOTIONS_2: [MessageHandler(Filters.text & ~Filters.command, emotions_2)],
            ENERGY: [MessageHandler(Filters.text & ~Filters.command, energy)],
            ENERGY_2: [MessageHandler(Filters.text & ~Filters.command, energy_2)],
            ATTENTION: [MessageHandler(Filters.text & ~Filters.command, attention)],
            ATTENTION_2: [MessageHandler(Filters.text & ~Filters.command, attention_2)],
            CONSCIENTIOUSNESS: [MessageHandler(Filters.text & ~Filters.command, conscientiousness)],
            CONSCIENTIOUSNESS_2: [MessageHandler(Filters.text & ~Filters.command, conscientiousness_2)],
            PROCRASTINATION: [MessageHandler(Filters.text & ~Filters.command, procrastination)],
            PROCRASTINATION_2: [MessageHandler(Filters.text & ~Filters.command, procrastination_2)],
            STRESS: [MessageHandler(Filters.text & ~Filters.command, stress)],
            STRESS_2: [MessageHandler(Filters.text & ~Filters.command, stress_2)],
            REGIME: [MessageHandler(Filters.text & ~Filters.command, regime)],
            REGIME_2: [MessageHandler(Filters.text & ~Filters.command, regime_2)],
            BODY: [MessageHandler(Filters.text & ~Filters.command, body)],
            BODY_2: [MessageHandler(Filters.text & ~Filters.command, body_2)],
            COMMENT: [MessageHandler(Filters.text & ~Filters.command, comment)],
            RATING: [MessageHandler(Filters.text & ~Filters.command, rating)],
            FINISH: [MessageHandler(Filters.regex('^(Save|Discard)$'), finish)]
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
