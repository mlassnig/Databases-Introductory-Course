# Hands-On Session 2

## Query plans

```
#!/usr/bin/python

import random
import time

import psycopg2 as pg

conn = pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")

conn.autocommit=False
cur = conn.cursor()
try: cur.execute('drop table large_table')
except: pass
conn.commit()
cur.execute('create table large_table (l char, s varchar(255), n int)')
conn.commit()
conn.autocommit=True

ts = time.time()
for i in xrange(1000000):
    if i%100 == 0:
        print i
    cur.execute("INSERT INTO large_table VALUES ('%s', '%s', %i)" % (chr(random.randrange(65, 91)),
                                                                     ''.join([chr(random.randrange(65, 91)) for i in xrange(1,16)]),
                                                                     random.randint(0,1000000)))
conn.commit()
print 'time taken:', time.time()-ts

conn.close()
```

```
set enable_seqscan=false;
```

```
select l, count(*) from large_table group by l;
select * from large_table where l='A';
```

```
create index idx_l on large_table(l);
```

```
create table large_table (l char, s varchar(255), n int)
 partition by range (n) (
 partition p0 values less than (500000),
 ...
 partition p1 values less than maxvalue
);

create table large_table (l char, s varchar(255), n int)
 partition by hash(n)
 partitions 10;
 ...

create table large_table (l char, s varchar(255), n int)
 partition by list(l) (
 partition p0 values in ('A', ... , 'L'),
 partition p1 values in ('M, ... , 'Z')
 ....
);
```

## Non-relational query optimisation

Edit ```vim /etc/kibana/kibana.yml``` and set ```server.host: 0.0.0.0```.

Afterwards ```service kibana restart```. You should now be able to access it on ```<hostname>:5601```

```
import json, pprint, random, datetime, time
import elasticsearch
es = elasticsearch.Elasticsearch()


ts = time.time()
for i in xrange(1000000):
    if i%100 == 0:
        print i
    es.index(index='large_index', doc_type='event',
             body=json.dumps({'timestamp': (datetime.datetime.now()+datetime.timedelta(seconds=i)).isoformat(),
                              'l': chr(random.randrange(65, 91)),
                              's': ''.join([chr(random.randrange(65, 91)) for i in xrange(1,16)]),
                              'n': random.randint(0,1000000)}))
print 'time taken:', time.time()-ts
```

```
import json, pprint, random, datetime, time
import elasticsearch
from elasticsearch import helpers

es = elasticsearch.Elasticsearch()


ts = time.time()
for i in xrange(1000):
    print i
    actions = [{'_index': 'large_index', '_type': 'event', '_source': {'timestamp': (datetime.datetime.now()+datetime.timedelta(seconds=i+j)).isoformat(),
                                                                                     'l': chr(random.randrange(65, 91)),
                                                                                     's': ''.join([chr(random.randrange(65, 91)) for i in xrange(1,16)]),
                                                                                     'n': random.randint(0,1000000)}} for j in xrange(1000)]
    helpers.bulk(es, actions)
print 'time taken:', time.time()-ts
```


## Transaction handling

```
create table tx_test (name varchar(4), money integer);

insert into tx_test values ('jack', 50);
insert into tx_test values ('jill', 100);
```

```
show transaction isolation level;
```

Terminal 1:

```
begin;
select money from tx_test where name='jack';
```

Terminal 2:

```
begin;
update tx_test set money=money-10 where name='jack';
commit;
```

Terminal 1:

```
select money from tx_test where name='jack';
```

Terminal 1:

```
set session characteristics as transaction isolation level repeatable read;
```

Terminal 2:

```
set session characteristics as transaction isolation level repeatable read;
```

Terminal 1:

```
begin;
select money from tx_test where name='jack';
```

Terminal 2:

```
begin;
update tx_test set money=money-10 where name='jack';
commit;
```

Terminal 1:

```
select money from tx_test where name='jack';
update tx_test set money=money+10 where name='jack';
```

Terminal 1:

```
set session characteristics as transaction isolation level read committed;
```

Terminal 2:

```
set session characteristics as transaction isolation level read committed;
```

Terminal 1:

```
begin;
```

Terminal 2:

```
begin;
```

Terminal 1:

```
update tx_test set money=money-10 where name='jack';
```

Terminal 2:

```
update tx_test set money=money+10 where name='jill';
```

Terminal 1:

```
update tx_test set money=money-20 where name='jill';
```

Terminal 2:

```
update tx_test set money=money+20 where name='jack';
```


## SQL Injection

```
CREATE TABLE users (id integer, login varchar(255), password varchar(255));
CREATE EXTENSION pgcrypto;
INSERT INTO users VALUES (0, 'root', crypt('hunter2', 'sha1'));
SELECT * FROM users;
```

```
#!/usr/bin/python

import random
import time

import psycopg2 as pg

conn = pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")

cur = conn.cursor()

login = raw_input('login: ')
password = raw_input('password: ')

print "select * from users where login=\'%s\' and password=crypt('%s', 'sha1')" % (login, password)

cur.execute("select * from users where login=\'%s\' and password=crypt('%s', 'sha1')" % (login, password))

if cur.fetchone():
    print 'logged in'
else:
    print 'wrong login or password'

cur.close()
conn.close()
```

```python sql_inject.py``` with username ```root``` and password ```hunter2```

Then inject with username ```root``` and password ```','sha1') or 1=1; update users set password=crypt('mypass', 'sha1'); commit; select 1;--```
