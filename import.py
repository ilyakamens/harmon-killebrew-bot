#!/usr/bin/env python

from datetime import date
import json
import pymysql.cursors
import sys

from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog <file_name>')
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        exit(1)

    names = set([line.strip() for line in open(args[0])])

    # load json config
    try:
        with open('config.json') as json_config:
            config = json.load(json_config)
    except Exception:
        sys.exit('Failed to open config.json')
    else:
        db_name = config['db_name']
        table_name = config['table_name']

    # connect to db
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 db=db_name,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # sql statement needs to be broken out, otherwise it breaks due to dynamic table name
            sql = "INSERT INTO `%s` " % table_name
            sql += "(`celeb`, `author`, `authored`) VALUES (%s, %s, %s)"
            for name in names:
                cursor.execute(sql, (name, 'IMPORT', str(date.today())))

        connection.commit()
    except Exception as e:
        sys.exit('Error importing celeb names.')
    finally:
        connection.close()
