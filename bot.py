#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

from telegram import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

import pandas as pd # xlsx table generation
import sqlite3 # database
import openpyxl # table shape adjustment

from replies import replies, help_text # bot's texts collection
import models # bot's database model


# Enable database
def init_db():
    engine = create_engine('sqlite:////root/telegram_bot/bot.db', echo=True)
    models.Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


def update_db(user, d):
    record = models.Record(
        user_id = user['id'],
        user_name = user['username'],
        datetime = datetime.now(),
        emotions = d.get('emotions',''),
        energy = d.get('energy',''),
        attention = d.get('attention',''),
        conscientiousness = d.get('conscientiousness',''),
        planning = d.get('planning',''),
        stress = d.get('stress',''),
        regime = d.get('regime',''),
        body = d.get('body',''),
        reading = d.get('reading',''),
        comment = d.get('comment',''),
        rating = int(d['rating'])
    )
    db_session.add(record)
    db_session.commit()


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
    adjust_cells_shape('report.xlsx')
    context.bot.send_document(chat_id=update.message.chat_id, document=open('report.xlsx', 'rb'))
    update.message.reply_text('''Вот ваш отчет''', reply_markup=entry_markup)
    return ConversationHandler.END


def adjust_cells_shape(xlsx_filepath):
    wb = openpyxl.load_workbook(filename = xlsx_filepath)        
    worksheet = wb.active
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = openpyxl.styles.Alignment(wrap_text=True,vertical='top')
    for col in worksheet.columns:
        column = col[0].column_letter
        if column == 'A':
            width = 15
        else:
            width = 30
        worksheet.column_dimensions[column].width = width
    wb.save(xlsx_filepath)


cancel_cmd = '/cancel'


def update_message(update, topic):
    message = replies[topic]['message']
    if len(replies[topic]['pairs']) > 0:
        reply_kb = [[x['key']] for x in replies[topic]['pairs']]
        reply_kb.append([cancel_cmd])
        markup = ReplyKeyboardMarkup(reply_kb, one_time_keyboard=True, resize_keyboard=True)
        update.message.reply_text(message, reply_markup=markup)
    else:
        update.message.reply_text(message)


def get_reply(msg,topic):
    default = replies[topic]['default_reply']
    for x in replies[topic]['pairs']:
        if msg == x['key']:
            return x['reply'] if len(x['reply']) > 0 else default
    return default


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

db_session = init_db()

EMOTIONS_2, EMOTIONS, ENERGY, ENERGY_2, ATTENTION, ATTENTION_2,\
    CONSCIENTIOUSNESS, CONSCIENTIOUSNESS_2, PLANNING, PLANNING_2,\
    STRESS, STRESS_2, REGIME, REGIME_2, BODY, BODY_2, READING, READING_2, COMMENT, RATING = range(20)


entry_reply_keyboard = [['/start_session'], ['/report', '/help']]
entry_markup = ReplyKeyboardMarkup(entry_reply_keyboard, one_time_keyboard=True, resize_keyboard=True)


def start(update, context):
    update.message.reply_text('''Это бот для отслеживания продуктивных состояний психики.''', reply_markup=entry_markup)
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(help_text, reply_markup=entry_markup)
    return ConversationHandler.END


def start_session(update, context):
    update_message(update, 'emotions')
    return EMOTIONS


def emotions(update, context):
    context.user_data['emotions'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'emotions'))
    return EMOTIONS_2


sep = ': '


def emotions_2(update, context):
    context.user_data['emotions'] += sep + update.message.text
    update_message(update, 'energy')
    return ENERGY


def energy(update, context):
    context.user_data['energy'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'energy'))
    return ENERGY_2


def energy_2(update, context):
    context.user_data['energy'] += sep + update.message.text
    update_message(update, 'attention')
    return ATTENTION


def attention(update, context):
    context.user_data['attention'] = update.message.text
    # TODO remove workaround
    #update.message.reply_text(get_reply(update.message.text,'attention'))
    #return ATTENTION_2
    update_message(update, 'conscientiousness')
    return CONSCIENTIOUSNESS


def attention_2(update, context):
    context.user_data['attention'] += sep + update.message.text
    update_message(update, 'conscientiousness')
    return CONSCIENTIOUSNESS


def conscientiousness(update, context):
    context.user_data['conscientiousness'] = update.message.text
    reply = get_reply(update.message.text,'conscientiousness')
    if reply == 'skip':
        update_message(update, 'planning')
        return PLANNING
    update.message.reply_text(reply)
    return CONSCIENTIOUSNESS_2


def conscientiousness_2(update, context):
    context.user_data['conscientiousness'] += sep + update.message.text
    update_message(update, 'planning')
    return PLANNING


def planning(update, context):
    context.user_data['planning'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'planning'))
    return PLANNING_2


def planning_2(update, context):
    context.user_data['planning'] += sep + update.message.text
    update_message(update, 'stress')
    return STRESS


def stress(update, context):
    context.user_data['stress'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'stress'))
    return STRESS_2


def stress_2(update, context):
    context.user_data['stress'] += sep + update.message.text
    update_message(update, 'regime')
    return REGIME


def regime(update, context):
    context.user_data['regime'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'regime'))
    return REGIME_2


def regime_2(update, context):
    context.user_data['regime'] += sep + update.message.text
    update_message(update, 'body')
    return BODY


def body(update, context):
    context.user_data['body'] = update.message.text
    # TODO remove workaround
    #update.message.reply_text(get_reply(update.message.text,'body'))
    #return BODY_2
    update_message(update, 'reading')
    return READING


def body_2(update, context):
    context.user_data['body'] += sep + update.message.text
    update_message(update, 'reading')
    return READING


def reading(update, context):
    context.user_data['reading'] = update.message.text
    update.message.reply_text(get_reply(update.message.text,'reading'))
    return READING_2


def reading_2(update, context):
    context.user_data['reading'] += sep + update.message.text
    update_message(update, 'comment')
    return COMMENT


def comment(update, context):
    context.user_data['comment'] = update.message.text
    update_message(update, 'rating')
    return RATING


def rating(update, context): #final question
    text = update.message.text
    if text.isdigit() and 0 <= int(text) <= 2:
        context.user_data['rating'] = int(text)
    else:
        update.message.reply_text('Введите 0, 1 или 2')
        return RATING

    update_db(update.message.from_user, context.user_data)
    context.user_data.clear()

    update.message.reply_text('''Спасибо! Таблицу с данными за все дни можно скачать по команде /report''', reply_markup=entry_markup)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the session.", user.first_name)
    update.message.reply_text('''Опрос отменен.''', reply_markup=entry_markup)
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
