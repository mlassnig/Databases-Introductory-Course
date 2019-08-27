#!/usr/bin/env python

from __future__ import print_function

import psycopg2 as pg

from multiprocessing import Process
from random import randint
from time import sleep

import loremipsum

# How often statistics is printed (in seconds)
UPDATE_PERIOD = 0.1

def get_row_count(cur):
    cur.execute('select count(*) from tw_challenge')
    return cur.fetchone()[0]

def get_session():
    return pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")


row_count_prev = [0]

while True:
    try:
        session = get_session()
        cur = session.cursor()

        row_count = get_row_count(cur)

        # Maintain least of previous row counts
        row_count_prev = row_count_prev[-5:]

        row_freq = row_count - row_count_prev[0]
        row_freq /= float(UPDATE_PERIOD) * len(row_count_prev)
        print()
        print('Row count = %6d' % row_count)
        print('Tweets per second = %6f' % row_freq)

        row_count_prev.append(row_count)

    except Exception as e:
        raise e
    finally:
        cur.close()
        session.close()

    sleep(UPDATE_PERIOD)

