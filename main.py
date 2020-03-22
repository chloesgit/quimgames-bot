#!/usr/bin/python
# -*- coding: utf-8 -*-

#from telegram.ext import Updater, CommandHandler
import requests
import re
import sqlite3
import datetime
import time
from configBot import token, chat_id, database

import telepot
from emoji import emojize

# Database
con = sqlite3.connect(database)
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
    bot.sendMessage(chat_id = chat_id, text=emojize("Ceci est un <b>test</b>", use_aliases=True), parse_mode='html')


def bot_add_points(bot, command):
    (points, player, sport) = command[3], command[1], command[2]
    sent_message = "Ajout de {0} points a {1} pour {2}".format(points, maj(player), sport)
    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        #print(timestamp)
        year = timestamp[:4]
        #print(year)
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", {1}, "{2}", "{3}", "{4}");'.format(timestamp, year, player, sport, points)
        cur.execute(requete)
    bot.sendMessage(chat_id = chat_id, text=sent_message)
    bot_table(bot, command)


def bot_remove_points(bot, command):
    (points, player) = -abs(int(command[2])), command[1]
    sent_message = "Penalite !\n{0} a pris une amende de {1} points...".format(player, points)
    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = int(timestamp[:4])
        requete = 'INSERT INTO tableauScore (timestamp, year, player, sport, points) VALUES ("{0}", {1}, "{2}", "Penalite", {3});'.format(timestamp, year, player, points)
        cur.execute(requete)
    bot.sendMessage(chat_id = chat_id, text=sent_message)
    bot_table(bot, command)


def bot_player(bot, command):
    player = command[1]
    
    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = int(timestamp[:4])
        requete = "SELECT sport, points FROM tableauScore WHERE tableauScore.year={0} AND tableauScore.player='{1}';".format(year, player)
        result = cur.execute(requete)
        score_list = result.fetchall()
        #print(score_list)
    
    sent_message = emojize("Scores de {}:\n\n".format(maj(player)), use_aliases=True)

    n = 0
    for (sport, points) in score_list:
        n += 1
        sent_message+="{} points pour {}\n".format(points, sport)
    
    bot.sendMessage(chat_id = chat_id, text=sent_message, parse_mode='Markdown')


def bot_leaderboard(bot, command):
    
    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = int(timestamp[:4])
        requete = 'SELECT player, sum(points) FROM tableauScore WHERE tableauScore.year = {0} GROUP BY player;'.format(year)
        scores_list = cur.execute(requete).fetchall()
        #print(scores_list)
        scores_list.sort(key=lambda x: x[1]) #Trie
        scores_list = scores_list[::-1] #Dans le bon ordre

    sent_message = ":trophy: *Classement general* :trophy:\n\n"
    n = 0
    for (player, points) in scores_list:
        n += 1
        sent_message+="{} - {} : {} points\n".format(n, maj(player), points)
    sent_message = emojize(sent_message, use_aliases=True)
    bot.sendMessage(chat_id = chat_id, text=sent_message, parse_mode='Markdown')

def bot_table(bot, command):
    
    conn = sqlite3.connect(database, timeout = 1000)
    with conn:
        cur = conn.cursor()
        timestamp = str(datetime.datetime.now())
        year = int(timestamp[:4])
        
        # Tableau General
        requete = 'SELECT player, sport, points FROM tableauScore WHERE tableauScore.year = {0};'.format(year)
        scores_list = cur.execute(requete).fetchall()
        scores_list.sort(key=lambda x: x[0]) #Trie
        liste_scores_players = organize(scores_list)
        
        # Totaux
        requete = 'SELECT player, sum(points) FROM tableauScore WHERE tableauScore.year = {0} GROUP BY player;'.format(year)
        totaux_list = cur.execute(requete).fetchall()
        totaux_list.sort(key=lambda x: x[1]) #Trie
        totaux_list = totaux_list[::-1] #Dans le bon ordre

        #Sports
        requete = 'SELECT * FROM tableauScore WHERE tableauScore.year = {0} GROUP BY sport;'.format(year)
        sports_list = select(cur.execute(requete).fetchall(), 3)
        sports_list.sort()
        
        #Debug
        #print("\nTotaux : ", totaux_list)
        #print("\nSports : ", sports_list)
        #print("\nGen : ",scores_list)
        print("\nTrié : ",liste_scores_players)
        #print("\nFind : ",find_points(liste_scores_players, "papa", sports_list))

    sent_message = ":trophy: *Recap general* :trophy:\n\n"
    sent_message += "``` Tot  Nom    "
    for item in sports_list:
        sent_message += maj(item[0])+" "
    sent_message += ""
    n = 0
    liste_emojis = ["🥇", "🥈", "🥉", "  ", "  ", "  ", "  ", "  ", "  ", "  "]
    for (player, points) in totaux_list:
        n += 1
        sent_message+="\n{}{} {} ".format(normal(points),liste_emojis[n-1], normal_name(maj(player)))
        for (sport, points_by_category) in find_points(liste_scores_players, player, sports_list):
            if points_by_category == 0:
                sent_message+="- "
            else:
                sent_message+="{} ".format(abs(points_by_category))
        sent_message += ""
    sent_message += "``` \n\n("
    for sport in sports_list:
        sent_message += "{} ".format(maj(sport))
    sent_message = emojize(sent_message+")", use_aliases=True)
    bot.sendMessage(chat_id = chat_id, text=sent_message, parse_mode='Markdown')


def maj(s):
    return s[0].upper()+s[1:].lower()

def normal(s):
    s = str(s)
    if len(s) < 2:
            return " "+s
    else:
            return s

def normal_name(s):
    if len(s) > 7:
            return s[:7]
    elif len(s) == 7:
        return s
    else:
            return normal_name(s+" ")

def organize(l):
    d = {}
    for item in l:
        if item[0] in d:
            print(d[item[0]])
            n = 0
            for (sport, _) in d[item[0]]:
                if sport == item[1]:
                    d[item[0]][n] = (d[item[0]][n][0], d[item[0]][n][1] + item[2])
                    break
                n += 1
            else:
                d[item[0]]+=[item[1:]]
        else:
            d[item[0]]=[item[1:]]
    list_by_player=list(d.items())
    #[x[n] for x in elements]
    return list_by_player

def find_points(l, player, sports):
    for item in l:
        if item[0] == player:
            liste = item[1]
    for sport in sports:
        for (sport_renseigne, _) in liste:
            if sport == sport_renseigne:
                break
        else:
            liste.append((sport, 0))
    liste.sort(key=lambda x: x[0])
    return liste

def select(l,index):
    ll=[]
    for item in l:
        ll.append(item[index])
    return ll

def handle(msg):
    if 'text' in msg:
        command = msg['text'].lower().replace('@', ' ').split(' ')
        if 'quimgames_bot' in command:
            command.remove('quimgames_bot')
    if command[0] in ['/test']:
        bot_testing(bot)
    elif command[0] in ['/ajouter']:
        if len(command) >= 4:
            bot_add_points(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/penalite']:
        if len(command) >= 3:
            bot_remove_points(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/score']:
        if len(command) >= 2:
            bot_player(bot, command)
        else:
            bot.sendMessage(chat_id = chat_id, text="Il manque des mots pour cette commande")
    elif command[0] in ['/general']:
        bot_leaderboard(bot, command)
    elif command[0] in ['/scores']:
        bot_table(bot, command)

try:
    bot = telepot.Bot(token)
    bot.message_loop(handle)
    #schedule.every(9*60+18).minutes.do(quote)
    print("QuimGames Bot lance !")

    while True:
        #schedule.run_pending()
        time.sleep(10)

except telepot.exception.TelegramError as err:
    print('{datetime} : Telegram Error'.format(datetime=datetime.datetime.now()))
    print(err)
