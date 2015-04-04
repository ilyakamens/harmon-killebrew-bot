#!/usr/bin/env python

import json
import MySQLdb
import pymysql.cursors
import sys

from optparse import OptionParser

if __name__ == '__main__':
    # get arguments
    parser = OptionParser(usage='usage: %prog <config_file.json>')
    (options, args) = parser.parse_args()

    # make sure we get the right number of args
    if len(args) != 1:
        parser.print_help()
        exit(1)

    # load json config
    try:
        with open(args[0]) as json_config:
            config = json.load(json_config)
    except Exception:
        sys.exit('Failed to open config file: %s' % args[0])
    else:
        db_name = config['db_name']
        table_name = config['table_name']

    # create database
    try:
        cursor = MySQLdb.connect(host='localhost', user='root').cursor()
        cursor.execute('CREATE DATABASE `%s`;' % db_name)
    except Exception as e:
        sys.exit('Error creating database')
    finally:
        cursor.close()

    # create table
    try:
        # connect to db
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     db=db_name,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection.cursor() as cursor:
            sql = "CREATE TABLE `%s` (celeb VARCHAR(30) NOT NULL PRIMARY KEY, author VARCHAR(30), authored DATE)" % table_name
            cursor.execute(sql)

        connection.commit()
    except Exception as e:
        import pdb
        pdb.set_trace()
        sys.exit('Error creating table')
    finally:
        connection.close()
