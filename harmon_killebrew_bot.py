#!/usr/bin/env python

import random
import re
import signal
import traceback

from hipster import Hipster
from optparse import OptionParser
from pprint import pprint
from time import sleep

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog <path to mixpanel-platform lib> (e.g. /home/username/mixpanel-platform)')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        exit(1)

    reviewer_ids = set([
        1355590,  # Ilya Kamens
    ])

    hipchat = Hipster('')
    room_id = 0000000
    last_date = None

    stopped = False
    def terminate(signum, frame):
        global stopped
        stopped = True
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    loaded_users = False
    while not loaded_users:
        response = hipchat.get_users_list()
        if response['status'] != 200:
            sleep(5)
            continue
        loaded_users = True
        users = response['data']['users']
    reviewers = {}
    for user in users:
        user_id = user['user_id']
        if user_id in reviewer_ids:
            reviewers[user_id] = user


    hipchat.send_messages(room_id=room_id, message='review_bot activated', sender='review_bot')

    while not stopped:
        try:
            messages = hipchat.get_messages(room_id=room_id, date='recent')
            for message in messages['data']['messages']:
                if last_date is not None and message['date'] > last_date:
                    message_text = message['message'].lower()
                    matches = re.findall('https://github.com/mixpanel/(?:analytics|mixpanel-\w+)/pull/\d+', message_text)
                    if message['from']['name'] != 'review_bot' and 'review' in message_text and matches:
                        possibles = reviewer_ids.difference([message['from']['user_id']])
                        reviewer = reviewers[random.choice(list(possibles))]
                        if len(matches) == 1:
                            text = '@%s selected to review %s' % (reviewer['mention_name'], matches[0])
                        else:
                            text = '@%s selected to review %d patches: %s' % (reviewer['mention_name'], len(matches), ' and '.join(matches))
                        hipchat.send_messages(room_id=room_id, message=text, message_format='text', sender='review_bot')
                    elif message_text.lower() == 'what is my user id?':
                        hipchat.send_messages(room_id=room_id, message=message['from']['user_id'], message_format='text', sender='user_id_bot')
            last_date = message['date']
        except:
            if 'messages' in locals():
                pprint(messages)
            print traceback.format_exc()
        sleep(5)

    hipchat.send_messages(room_id=room_id, message='review_bot deactivated', sender='review_bot')
