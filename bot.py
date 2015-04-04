#!/usr/bin/env python

import json
import pymysql.cursors
import signal
import string
import sys
import traceback

from datetime import date
from hipster import Hipster
from optparse import OptionParser
from pprint import pprint
from time import sleep

# terminate process
def terminate(signum, frame):
    global stopped
    stopped = True
    connection.close()
    send_message('killebrew_bot deactivated :(')
signal.signal(signal.SIGTERM, terminate)
signal.signal(signal.SIGINT, terminate)

def add_word(celeb, said_by):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `names` (`celeb`, `said_by`, `date_said`) VALUES (%s, %s, %s)"
            result = cursor.execute(sql, (celeb, said_by, str(date.today())))

        connection.commit()
    except Exception as e:
        if str(e.args[0]) == '1062':
            send_message('No!')
        else:
            send_message('Error %s: %s' % (e.args[0], e.args[1]))
    else:
        split = celeb.split(' ', 1)
        dubdub_text = ''
        if len(split) > 1 and split[0][0] == split[1][0]:
            global order
            order = -order
            dubdub_text = 'DUB DUB! '

        next_player_index = (player_list.index(said_by) + order) % len(player_list)
        global current_player
        current_player = player_list[next_player_index]
        send_message('%sNew entry # %s! %s said by %s on %s. Next player is %s.' % (dubdub_text,
                                                                                    result,
                                                                                    celeb,
                                                                                    said_by,
                                                                                    str(date.today()),
                                                                                    player_map[current_player]['mention_name']))

def send_message(text):
    hipchat.send_messages(room_id=room_id, message=text, sender='killebrew_bot')

if __name__ == '__main__':
    # get arguments
    parser = OptionParser(usage='usage: %prog <api_token> <room_id> <database> <userlist.json>')
    (options, args) = parser.parse_args()

    # make sure we get the right number of args
    if len(args) != 4:
        parser.print_help()
        exit(1)

    hipchat = Hipster(args[0])
    room_id = args[1]

    # connect to db
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 db=args[2],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # get users in hipchat room
    while True:
        response = hipchat.get_users_list()
        if response['status'] == 200:
            users = response['data']['users']
            break
        else:
            sleep(5)
            continue

    # open user list file
    try:
        with open(args[3]) as user_list_file:
            player_list = json.load(user_list_file)
    except Exception:
        connection.close()
        error_message = 'Failed to open user list file: %s' % args[3]
        send_message(error_message)
        sys.exit(error_message)

    # create user map
    player_map = {}
    for user in users:
        if user['name'] in player_list:
            player_map[user['name']] = user

    # say hi to chat! kind of shitty, but this needs to be here
    # so the bot doesn't ignore the first message
    send_message('killebrew_bot activated :)')

    last_date = None
    stopped = False
    order = 1
    current_player = None
    while not stopped:
        try:
            messages = hipchat.get_messages(room_id=room_id, date='recent')
            for message in messages['data']['messages']:
                if last_date is not None and message['date'] > last_date:
                    message_text = message['message'].lower()
                    said_by = message['from']['name']
                    if '(upvote)' in message_text and current_player == said_by:
                        celeb = message_text.replace('(upvote)', '').strip()
                        add_word(celeb, said_by)
                    elif message_text == 'reverse order' and said_by == 'Ilya Kamens':
                        order = -order
                        send_message('Order reversed')
                    elif 'set current player:' in message_text and said_by == 'Ilya Kamens':
                        current_player = string.capwords(message_text.replace('set current player:', '').strip())
                        send_message('Current player is %s' % player_map[current_player]['mention_name'])

            last_date = message['date']
        except:
            if 'messages' in locals():
                pprint(messages)
            print traceback.format_exc()
        sleep(10)
