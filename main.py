#from telegram.ext import Updater, CommandHandler
import requests
import re
import sqlite3
import datetime
import time

import telepot

# Configuration
token = '912339355:AAEp_47mRVri9kDRfjWdJIGKTdizrNHM0YY'
#chat_id = '-1001433683644' #Kwala Familia
chat_id = '-325590372' #Bot Testing

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
def bot_testing(bot):
    bot.sendMessage(chat_id = chat_id, text="Ceci est un test")

def bot_add_points(bot, command):
    (points, player, sport) = command[3], command[1], command[2]
    sent_message = "Ajout de {0} points a {1} pour {2}".format(points, player, sport)
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        print(timestamp)
        year = timestamp[:4]
        print(year)
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", "{1}", "{2}", "{3}", "{4}");'.format(timestamp, year, player, sport, points)
        cur.execute(requete)
    bot.sendMessage(chat_id = chat_id, text=sent_message)

def bot_look_points(bot, command):
    player = command[1]
    
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = timestamp[:4]
        #requete = 'SELECT (sport, points) FROM tableauScore WHERE year={0} AND player={1}'.format(year, player)
        requete = 'SELECT distinct(sport, points) FROM tableauScore WHERE tableauScore.year = {0} ;'.format(year)
        result_fetched = cur.execute(requete).fetchone()
        print(result_fetched)
    sent_message = "{} a des points !".format(player)
    bot.sendMessage(chat_id = chat_id, text=sent_message)

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
    if 'text' in msg:
        command = msg['text'].split(' ')
    if command[0] in ['/test']:
        print(command)
        bot_testing(bot)
    elif command[0] in ['/ajouter']:
        print(command)
        bot_add_points(bot, command)
    elif command[0] in ['/regarder']:
        print(command)
        bot_look_points(bot, command)

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
