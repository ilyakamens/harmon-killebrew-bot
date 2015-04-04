#!/usr/bin/env python

import json
import MySQLdb
import pymysql.cursors
import sys

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
