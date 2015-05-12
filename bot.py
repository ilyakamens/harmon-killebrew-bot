#!/usr/bin/env python

import json
import pymysql.cursors
import signal
import sys
import traceback

from datetime import date
from hipster import Hipster
from pprint import pprint
from time import sleep

class HKBot:
    def __init__(self):
        # load json config
        try:
            with open('config.json') as json_config:
                config = json.load(json_config)
        except Exception:
            sys.exit('Failed to open config.json')
        self.db_name = config['db_name']
        self.table_name = config['table_name']
        self.player_list = [player.lower() for player in config['player_list']]
        self.super_user = config['super_user'].lower()
        self.hipchat = Hipster(config['api_key'])
        self.room_id = config['room_id']
        self.order = 1
        self.current_player = self.super_user

        # connect to db
        self.connection = self.get_mysql_connection(self.db_name)

        # get users in hipchat room
        while True:
            response = self.hipchat.get_users_list()
            if response['status'] == 200:
                users = response['data']['users']
                break
            else:
                sleep(5)
                continue

        # create user map
        self.player_map = {}
        for user in users:
            if user['name'].lower() in self.player_list:
                self.player_map[user['name'].lower()] = user

    def start(self):
        # say hi to chat! kind of shitty, but this needs to be here
        # so the bot doesn't ignore the first message
        self.send_message('killebrew_bot activated :)')
        last_date = None
        while True:
            try:
                messages = self.hipchat.get_messages(room_id=self.room_id, date='recent')
                for message in messages['data']['messages']:
                    if last_date is not None and message['date'] > last_date:
                        message_text = message['message'].lower()
                        author = message['from']['name'].lower()
                        if '(upvote)' in message_text and self.current_player == author:
                            full_celeb = message_text.replace('(upvote)', '').strip().split(' ')
                            full_celeb = ' '.join([word for word in full_celeb if '@' not in word])
                            # eliminate double letters so celebrities can be written in
                            # the Announcer Voice (e.g., HARRRMOONNNNN KILLLEBREEWWWWW) :)
                            # celeb = ' '
                            # i = 0
                            # for letter in full_celeb:
                            #     if letter == celeb[i]:
                            #         pass
                            #     else:
                            #         celeb += letter
                            #         i += 1
                            # celeb = celeb[1:]
                            # self.add_word(celeb, author)
                            self.add_word(full_celeb, author)
                        elif message_text == 'reverse order' and author == self.super_user:
                            self.order = -self.order
                            self.send_message('Order reversed')
                        elif 'set current player:' in message_text and author == self.super_user:
                            self.current_player = message_text.replace('set current player:', '').strip()
                            self.send_message('Current player is @%s' % self._get_current_player_mention_name())
                        elif '(downvote)' in message_text and author == self.super_user:
                            full_deleted_celeb = message_text.replace('(downvote)', '').strip()
                            # deleted_celeb = ' '
                            # i = 0
                            # for letter in full_deleted_celeb:
                            #     if letter == deleted_celeb[i]:
                            #         pass
                            #     else:
                            #         deleted_celeb += letter
                            #         i += 1
                            # deleted_celeb = deleted_celeb[1:]
                            # self.del_word(deleted_celeb)
                            self.del_word(full_deleted_celeb)
                        elif message_text == "who's next" and author == self.super_user:
                            self.send_message(self._get_next_player_name() + '. fresh like uhhh')
                        elif message_text == "skip" and author == self.super_user:
                            self.current_player = self._get_next_player_name()
                            self.send_message('too slow bro. current player isssssss %s' % self._get_current_player_mention_name())
                last_date = message['date']
            except:
                if 'messages' in locals():
                    pprint(messages)
                print traceback.format_exc()
            sleep(10)

    def get_mysql_connection(self, db_name):
        return pymysql.connect(host='localhost',
                               user='root',
                               db=db_name,
                               charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)

    def send_message(self, text):
        self.hipchat.send_messages(room_id=self.room_id, message=text, message_format='text', sender='killebrew_bot')

    def _get_current_player_mention_name(self):
        return '@' + self.player_map[self.current_player]['mention_name']

    def _get_next_player_name(self):
        next_player_index = (self.player_list.index(self.current_player) + self.order) % len(self.player_list)
        return self.player_list[next_player_index]

    def add_word(self, celeb, author):
        try:
            with self.connection.cursor() as cursor:
                # sql statement needs to be broken out, otherwise it breaks due to dynamic table name
                sql = ''.join(["INSERT INTO `%s` " % self.table_name, "(`celeb`, `author`, `authored`) VALUES (%s, %s, %s)"])
                cursor.execute(sql, (celeb, author, str(date.today())))

            self.connection.commit()
        except Exception as e:
            # celeb was already said
            if str(e.args[0]) == '1062':
                self.send_message('No!')
            # connection to mysql was droppped; re-connect and try again
            elif str(e.args[0]) == '2006':
                self.connection = self.get_mysql_connection(self.db_name)
                return self.add_word(celeb, author)
            else:
                self.send_message('Error %s: %s' % (e.args[0], e.args[1]))
        else:
            split = celeb.split(' ', 1)
            dubdub_text = ''
            if len(split) > 1 and split[0][0] == split[1][0]:
                self.order = -self.order
                dubdub_text = 'DUB DUB! '
            self.current_player = self._get_next_player_name()
            self.send_message('%s"%s" said by %s on %s. Next player is @%s!' % (dubdub_text,
                                                                                celeb,
                                                                                author,
                                                                                str(date.today()),
                                                                                self._get_current_player_mention_name()))

    def del_word(self, celeb):
        author = None
        try:
            with self.connection.cursor() as cursor:
                sql1 = ''.join(["SELECT `author` FROM `%s` " % self.table_name, "WHERE `celeb` = %s"])
                cursor.execute(sql1, (celeb))
                row = cursor.fetchone()
                if (row):
                    author = row['author']
                else:
                    self.send_message('%s was never said!' % celeb)

            self.connection.commit()
        except Exception as e:
            if str(e.args[0]) == 'xxxx': # would this be an error? where the row we want to delete does not exist?
                self.send_message('%s was never said!' % celeb)
            # connection to mysql was droppped; re-connect and try again
            elif str(e.args[0]) == '2006':
                self.connection = self.get_mysql_connection(self.db_name)
                return self.del_word(celeb)
            else:
                self.send_message('Error %s' % (e))
        else:
            try:
                with self.connection.cursor() as cursor:
                    sql = ''.join(["DELETE FROM `%s` " % self.table_name, "WHERE `celeb` = %s"])
                    cursor.execute(sql, (celeb))

                self.connection.commit()
            except Exception as e:
                if str(e.args[0]) == 'xxxx': # would this be an error? where the row we want to delete does not exist?
                    self.send_message('%s was never said!' % celeb)
                # connection to mysql was droppped; re-connect and try again
                elif str(e.args[0]) == '2006':
                    self.connection = self.get_mysql_connection(self.db_name)
                    return self.del_word(celeb)
                else:
                    self.send_message('Error %s: %s' % (e.args[0], e.args[1]))
            else:
                self.current_player = self.player_list[self.player_list.index(author)]
                self.send_message('%s deleted. @%s is still up!' % (celeb,
                                                                    self._get_current_player_mention_name()))

    # terminate process
    def terminate(self, signum, frame):
        self.connection.close()
        self.send_message('killebrew_bot deactivated :(')
        sys.exit(0)

if __name__ == '__main__':
    bot = HKBot()
    signal.signal(signal.SIGTERM, bot.terminate)
    signal.signal(signal.SIGINT, bot.terminate)
    bot.start()
