#from telegram.ext import Updater, CommandHandler
import requests
import re
import sqlite3
import datetime
import time

import telepot

# Configuration
token = '912339355:AAEuBF_UbbJskNUTvHIUwTDZsNijJxEKwzE'
chat_id = '-1001433683644' #Kwala Familia

# Database
con = sqlite3.connect('scores.db')
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS tableauScore (
    timestamp text PRIMARY KEY,
    year int,
    player text,
    sport text,
    points int,
    info text
);""")
con.commit()


# Commands
def classement(bot, update):
    chat_id = update.message.chat_id

    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'SELECT add(*) from tableauScore where annee = "{}" groupby player;'.format(str(datetime.datetime.now())[:4])
        result = cur.execute(requete).fetchone()

        sent_message = result

        bot.send_message(chat_id=chat_id, text=sent_message, parse_mode='Markdown')

def score(bot, update, player):
    chat_id = update.message.chat_id

    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'SELECT * from tableauScore where annee = "{0}" and player = "{1}";'.format(str(datetime.datetime.now())[:4], player)
        result = cur.execute(requete).fetchone()

        sent_message = result
        bot.send_message(chat_id=chat_id, text=sent_message, parse_mode='Markdown')

def points(bot, update, player, sport, points):
    chat_id = update.message.chat_id
    sent_message = "Ajout de {0} points a {1} pour {2}".format(points, player, sport)
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}");'.format(str(datetime.datetime.now()), str(str(datetime.datetime.now())[:4]), player, sport, points)
        cur.execute(requete)
    bot.send_message(chat_id=chat_id, text=sent_message, parse_mode='Markdown')

def penalite(bot, update, player, points):
    chat_id = update.message.chat_id
    sent_message = "Penalite de {0} points a {1} !".format(points, player)

    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", "{1}", "{2}", "Penalite", "{3}");'.format(str(datetime.datetime.now()), str(datetime.datetime.now()[:4]), player, -points)
        cur.execute(requete)
    bot.send_message(chat_id=chat_id, text=sent_message, parse_mode='Markdown')


"""
def main():
    updater = Updater("912339355:AAEuBF_UbbJskNUTvHIUwTDZsNijJxEKwzE", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('classement', classement))
    dp.add_handler(CommandHandler('score', score))
    dp.add_handler(CommandHandler('points', points))
    dp.add_handler(CommandHandler('penalite', penalite))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
"""
def handle(msg):
    print(msg)
    #
    #if msg['text'].split(' ')[0] in ['/add']:
    #    command = command.split('@')[0]
    #    bot.sendMessage(msg['text'])

try:
    bot = telepot.Bot(token)
    bot.message_loop(handle)
    #schedule.every(9*60+18).minutes.do(quote)
    print("QuimGames Bot lancé !")

    while True:
        #schedule.run_pending()
        time.sleep(1000)

except telepot.exception.TelegramError as err:
    print('{datetime} : Telegram Error'.format(datetime=datetime.datetime.now()))
    print(err)
