#!/usr/bin/env python

import json
import pymysql.cursors
import signal
import string
import sys
import traceback

from datetime import date
from hipster import Hipster
from pprint import pprint
from time import sleep

# terminate process
def terminate(signum, frame):
    connection.close()
    send_message('killebrew_bot deactivated :(')
    sys.exit(0)
signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGINT, terminate)

def get_mysql_connection(db_name):
    return pymysql.connect(host='localhost',
                           user='root',
                           db=db_name,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

def add_word(celeb, author):
    try:
        with connection.cursor() as cursor:
            # sql statement needs to be broken out, otherwise it breaks due to dynamic table name
            sql = ''.join(["INSERT INTO `%s` " % table_name, "(`celeb`, `author`, `authored`) VALUES (%s, %s, %s)"])
            cursor.execute(sql, (celeb, author, str(date.today())))

        connection.commit()
    except Exception as e:
        if str(e.args[0]) == '1062':
            send_message('No!')
        elif str(e.args[0]) == '2006':
            global connection
            connection = get_mysql_connection(db_name)
            return add_word(celeb, author)
        else:
            send_message('Error %s: %s' % (e.args[0], e.args[1]))
    else:
        split = celeb.split(' ', 1)
        dubdub_text = ''
        if len(split) > 1 and split[0][0] == split[1][0]:
            global order
            order = -order
            dubdub_text = 'DUB DUB! '

        next_player_index = (player_list.index(author) + order) % len(player_list)
        global current_player
        current_player = player_list[next_player_index]
        send_message('%s"%s" said by %s on %s. Next player is @%s!' % (dubdub_text,
                                                                       celeb,
                                                                       author,
                                                                       str(date.today()),
                                                                       player_map[current_player]['mention_name']))

def del_word(celeb):
    author = None
    try:
        with connection.cursor() as cursor:
            sql1 = ''.join(["SELECT `author` FROM `%s` " % table_name, "WHERE `celeb` = %s"])
            cursor.execute(sql1, (celeb))
            row = cursor.fetchone()
            if (row):
                author = row['author']
            else:
                send_message('%s was never said!' % celeb)

        connection.commit()
    except Exception as e:
        if str(e.args[0]) == 'xxxx': # would this be an error? where the row we want to delete does not exist?
            send_message('%s was never said!' % celeb)
        elif str(e.args[0]) == '2006':
            global connection
            connection = get_mysql_connection(db_name)
            return del_word(celeb)
        else:
            send_message('Error %s' % (e))
    else:
        try:
            with connection.cursor() as cursor:
                sql = ''.join(["DELETE FROM `%s` " % table_name, "WHERE `celeb` = %s"])
                cursor.execute(sql, (celeb))

            connection.commit()
        except Exception as e:
            if str(e.args[0]) == 'xxxx': # would this be an error? where the row we want to delete does not exist?
                send_message('%s was never said!' % celeb)
            elif str(e.args[0]) == '2006':
                global connection
                connection = get_mysql_connection(db_name)
                return del_word(celeb)
            else:
                send_message('Error %s: %s' % (e.args[0], e.args[1]))
        else:
            player_index = player_list.index(author)
            current_player = player_list[player_index]
            send_message('%s deleted. @%s is still up!' % (celeb, 
                                                           player_map[current_player]['mention_name']))


def send_message(text):
    hipchat.send_messages(room_id=room_id, message=text, message_format='text', sender='killebrew_bot')

if __name__ == '__main__':
    # load json config
    try:
        with open('config.json') as json_config:
            config = json.load(json_config)
    except Exception:
        sys.exit('Failed to open config.json')
    else:
        db_name = config['db_name']
        table_name = config['table_name']
        player_list = config['player_list']
        super_user = string.capwords(config['super_user'])
        hipchat = Hipster(config['api_key'])
        room_id = config['room_id']

    # connect to db
    connection = get_mysql_connection(db_name)

    # get users in hipchat room
    while True:
        response = hipchat.get_users_list()
        if response['status'] == 200:
            users = response['data']['users']
            break
        else:
            sleep(5)
            continue

    # create user map
    player_map = {}
    for user in users:
        if user['name'] in player_list:
            player_map[user['name']] = user

    # say hi to chat! kind of shitty, but this needs to be here
    # so the bot doesn't ignore the first message
    send_message('killebrew_bot activated :)')

    last_date = None
    order = 1
    current_player = None
    while True:
        try:
            messages = hipchat.get_messages(room_id=room_id, date='recent')
            for message in messages['data']['messages']:
                if last_date is not None and message['date'] > last_date:
                    message_text = message['message'].lower()
                    author = message['from']['name']
                    if '(upvote)' in message_text and current_player == author:
                        full_celeb = message_text.replace('(upvote)', '').strip().split(' ')
                        full_celeb = ' '.join([word for word in full_celeb if '@' not in word])
                        # eliminate double letters so celebrities can be written in 
                        # the Announcer Voice (e.g., HARRRMOONNNNN KILLLEBREEWWWWW) :)
                        celeb = ' '
                        i = 0
                        for letter in full_celeb:
                            if letter == celeb[i]:
                                pass
                            else:
                                celeb += letter
                                i += 1
                        celeb = celeb[1:]
                        add_word(celeb, author)
                    elif message_text == 'reverse order' and author == super_user:
                        order = -order
                        send_message('Order reversed')
                    elif 'set current player:' in message_text and author == super_user:
                        current_player = string.capwords(message_text.replace('set current player:', '').strip())
                        send_message('Current player is @%s' % player_map[current_player]['mention_name'])
                    elif '(downvote)' in message_text and author == super_user:
                        full_deleted_celeb = string.capwords(message_text.replace('(downvote)', '').strip())
                        deleted_celeb = ' '
                        i = 0
                        for letter in full_deleted_celeb:
                            if letter == deleted_celeb[i]:
                                pass
                            else:
                                deleted_celeb += letter
                                i += 1
                        deleted_celeb = deleted_celeb[1:]
                        del_word(deleted_celeb)

            last_date = message['date']
        except:
            if 'messages' in locals():
                pprint(messages)
            print traceback.format_exc()
        sleep(30)
