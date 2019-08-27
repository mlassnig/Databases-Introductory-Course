#!/usr/bin/python

from __future__ import print_function

import psycopg2 as pg

from multiprocessing import Process
from random import randint
from time import sleep

import loremipsum

def get_session():
    return pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")

def bootstrap_tables():
    session = get_session()
    cur = session.cursor()
    try:
        print('trying to create new table')
        cur.execute('''
        create table tw_challenge (
            msg varchar(511),
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        ''')
    except:
        session.rollback()
        print('table already existed, truncating instead')
        cur.execute('truncate table tw_challenge')
    cur.close()
    session.commit()

def insert_rows():
    while True:
        session = get_session()
        cur = session.cursor()
        message = loremipsum.generate_sentence()[2]
        cur.execute('insert into tw_challenge VALUES (%s)', (message, ))
        session.commit()
        cur.close()
        session.close()
        sleep(0.1)

def print_random():
    sleep(1)
    while True:
        session = get_session()
        cur = session.cursor()
        cur.execute('SELECT msg FROM tw_challenge ORDER BY '
        'random() LIMIT 5;')
        rand_msgs = [x[0] for x in cur.fetchall()]
        print('random:\n ', '\n  '.join(rand_msgs))
        cur.close()
        session.close()
        sleep(2)

def print_latest():
    while True:
        session = get_session()
        cur = session.cursor()
        cur.execute('SELECT msg FROM tw_challenge ORDER BY '
        'timestamp DESC LIMIT 10;')
        latest_msgs = [x[0] for x in cur.fetchall()]
        print('latest:\n ', '\n  '.join(latest_msgs))
        cur.close()
        session.close()
        sleep(2)

if __name__ == '__main__':
    bootstrap_tables()

    processes_to_start = [
        insert_rows,
        print_latest,
        print_random
    ]

    # Create 10 processes of each given type
    proc_list = [ Process(target=func) for func in processes_to_start for i in range(10) ]

    for proc in proc_list:
        proc.start()
    for proc in proc_list:
        proc.join()

