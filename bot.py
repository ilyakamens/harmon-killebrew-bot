#!/usr/bin/env python

import pymysql.cursors
import signal
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
        send_message('New entry # %s! %s said by %s on %s' % (result, celeb, said_by, str(date.today())))

def send_message(text):
    hipchat.send_messages(room_id=room_id, message=text, sender='killebrew_bot')

if __name__ == '__main__':
    # get arguments
    parser = OptionParser(usage='usage: %prog <api_token> <room_id> <database>')
    (options, args) = parser.parse_args()

    # make sure we get the right number of args
    if len(args) != 3:
        parser.print_help()
        exit(1)

    hipchat = Hipster(args[0])
    room_id = args[1]

    player_ids = set([
        1355590, # Ilya Kamens
        1022218, # Diggory Rycroft
        1710903  # Laura Del Beccaro
    ])

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
    players = {}
    for user in users:
        user_id = user['user_id']
        if user_id in player_ids:
            players[user_id] = user

    # connect to db
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 db=args[2],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # say hi to chat! kind of shitty, but this needs to be here
    # so the bot doesn't ignore the first message
    send_message('killebrew_bot activated :)')

    last_date = None
    stopped = False
    while not stopped:
        try:
            messages = hipchat.get_messages(room_id=room_id, date='recent')
            for message in messages['data']['messages']:
                if last_date is not None and message['date'] > last_date:
                    message_text = message['message'].lower()
                    if '(upvote)' in message_text:
                        celeb = message_text.replace('(upvote)', '').strip()
                        said_by = message['from']['name']
                        add_word(celeb, said_by)
                    elif message_text == 'id please':
                        send_message(str(message['from']['user_id']))
            last_date = message['date']
        except:
            if 'messages' in locals():
                pprint(messages)
            print traceback.format_exc()
        sleep(10)
