#from telegram.ext import Updater, CommandHandler
import requests
import re
import sqlite3
import datetime
import time
from configBot import token, chat_id

import telepot
from emoji import emojize

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
    bot.sendMessage(chat_id = chat_id, text="Ceci est un *test*", parse_mode='Markdown')

def bot_add_points(bot, command):
    (points, player, sport) = command[3], command[1], command[2]
    sent_message = "Ajout de {0} points a {1} pour {2}".format(points, maj(player), sport)
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

def bot_remove_points(bot, command):
    (points, player) = str(-abs(int(command[2]))), command[1]
    sent_message = "Pénalité !\n{0} a pris une amende de {1} points...".format(player, points,)
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = timestamp[:4]
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", "{1}", "{2}", "Penalite", "{3}");'.format(timestamp, year, player, points)
        cur.execute(requete)
    bot.sendMessage(chat_id = chat_id, text=sent_message)

def bot_player(bot, command):
    player = command[1]
    
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = timestamp[:4]
        requete = "SELECT sport, points FROM tableauScore WHERE tableauScore.year={0} AND tableauScore.player='{1}';".format(year, player)
        result = cur.execute(requete)
        print(result)
        result_fetched = result.fetchone()
        print(result_fetched)
    sent_message = emojize("Scores de {}:\nblah".format(player), use_aliases=True)
    bot.sendMessage(chat_id = chat_id, text=sent_message)

def bot_leaderboard(bot, command):
    
    conn = sqlite3.connect('scores.db', timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = timestamp[:4]
        requete = 'SELECT player, sum(points) FROM tableauScore WHERE tableauScore.year = {0} GROUP BY player;'.format(year)
        scores_list = cur.execute(requete).fetchall()
        print(scores_list)
        scores_list.sort(key=lambda x: x[1]) #Trie
        scores_list = scores_list[::-1] #Dans le bon ordre

    sent_message = ":trophy: *Classement général* :trophy:\n\n"
    n = 0
    for (player, points) in scores_list:
        n += 1
        sent_message+="{} - {} : {} points\n".format(n, maj(player), points)
    sent_message = emojize(sent_message, use_aliases=True)
    bot.sendMessage(chat_id = chat_id, text=sent_message, parse_mode='Markdown')

def maj(s):
    return s[0].upper()+s[1:].lower()


def handle(msg):
    print(msg)
    if 'text' in msg:
        command = msg['text'].lower().replace('@', ' ').split(' ')
        if 'quimgames_bot' in command:
            command.remove('quimgames_bot')
    if command[0] in ['/test']:
        print(command)
        bot_testing(bot)
    elif command[0] in ['/ajouter']:
        print(command)
        if len(command) >= 4:
            bot_add_points(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/penalite']:
        print(command)
        if len(command) >= 3:
            bot_remove_points(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/score']:
        print(command)
        if len(command) >= 2:
            bot_player(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/scores']:
        print(command)
        bot_leaderboard(bot, command)

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
