# Challenge

## Fake Twitter Template
```
#!/usr/bin/python

import psycopg2 as pg

from multiprocessing import Process
from random import randint
from time import sleep

def get_session():
    return pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")

def bootstrap_tables():
    session = get_session()
    cur = session.cursor()
    try:
        print 'trying to create new table'
        cur.execute('create table mp_test (value integer)')
    except:
        print 'table alread existed, truncating instead'
        cur.execute('truncate table mp_test')
    cur.close()
    session.commit()

def insert_rows():
    while True:
        print 'inserting'
        session = get_session()
        cur = session.cursor()
        cur.execute('insert into mp_test values (%s)', [randint(0,9)])
        session.commit()
        cur.close()
        session.close()
        sleep(0.1)

def delete_rows():
    while True:
        print 'deleting'
        session = get_session()
        cur = session.cursor()
        cur.execute('delete from mp_test where value = %s', [randint(0,9)])
        session.commit()
        cur.close()
        session.close()
        sleep(0.1)

def count_rows():
    while True:
        session = get_session()
        cur = session.cursor()
        cur.execute('select count(*) from mp_test')
        res = cur.fetchone()
        print 'rows', res[0]
        cur.close()
        session.close()
        sleep(1)

if __name__ == '__main__':
    bootstrap_tables()
    p_inserter = Process(target=insert_rows)
    p_deleter = Process(target=delete_rows)
    p_counter = Process(target=count_rows)
    p_inserter.start()
    p_deleter.start()
    p_counter.start()
    p_inserter.join()
    p_deleter.join()
    p_counter.join()


