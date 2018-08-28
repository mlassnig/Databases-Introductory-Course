# Hands-On Session 1

## PostgreSQL


```vim /etc/postgresql/9.5/main/pg_hba.conf```

Set all to ```trust```, then add this line ```host all all 0.0.0.0/0 trust```

```service postgresql restart```

Should not ask for password, and you can quit with ```ctrl-d```

```
sudo -u postgres /usr/bin/psql -c "CREATE ROLE gridka01 PASSWORD 'asdf1234' SUPERUSER CREATEDB CREATEROLE INHERIT LOGIN;"
sudo -u postgres /usr/bin/psql -c "CREATE DATABASE gridka_db OWNER gridka01 ENCODING 'UTF8'"
sudo -u postgres /usr/bin/psql -d gridka_db -c "CREATE SCHEMA gridka_schema AUTHORIZATION gridka01"
sudo -u postgres /usr/bin/psql -d gridka_db -c "GRANT ALL ON SCHEMA gridka_schema TO gridka01"
sudo -u postgres /usr/bin/psql -d gridka_db -c "GRANT ALL ON DATABASE gridka_db TO gridka01"
```

```ls -la /var/lib/postgresql/9.5/```

```psql -U gridka01 gridka_db```

```vim /etc/postgresql/9.5/main/pg_hba.conf```

Set all to ```md5```

```psql -U gridka01 gridka_db```

Should now ask for password.


```psql -U gridka01 gridka_db```


```\l``` .. list all databases

```\d``` .. list all relations

```
CREATE TABLE test_table ( first_name VARCHAR, last_name VARCHAR );

\d

SELECT * FROM test_table;

INSERT INTO test_table VALUES ('Vincent', 'Vega');

SELECT * FROM test_table;

INSERT INTO test_table (last_name, first_name) VALUES ('Jules', 'Winnfield');

SELECT * FROM test_table;

DELETE FROM test_table;

SELECT * FROM test_table;

DROP TABLE test_table;

SELECT * FROM test_table;
```

```
#include <stdio.h>
#include <stdlib.h>

#include <libpq-fe.h>

int main()
{
        PGconn *conn;
        conn = PQconnectdb("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'");
        if (PQstatus(conn) != CONNECTION_OK) {
                printf("%s\n", PQerrorMessage(conn));
                exit(1);
        }

        PGresult *res;
        res = PQexec(conn, "CREATE TABLE test_table ( first_name VARCHAR, last_name VARCHAR )");
        if (!res)
                printf("%s\n", PQerrorMessage(conn));
        PQclear(res);

        res = PQexec(conn, "INSERT INTO test_table VALUES ( 'Vincent', 'Vega' )");
        if (!res)
                printf("%s\n", PQerrorMessage(conn));
        PQclear(res);

        res = PQexec(conn, "INSERT INTO test_table (last_name, first_name) VALUES ( 'Jules', 'Winnfield' )");
        if (!res)
                printf("%s\n", PQerrorMessage(conn));
        PQclear(res);

        res = PQexec(conn, "SELECT * FROM test_table");
        if (PQresultStatus(res) == PGRES_TUPLES_OK)
                for(int i = 0; i < PQntuples(res); ++i)
                        printf("%s %s\n", PQgetvalue(res, i, 0), PQgetvalue(res, i, 1));
        else
                printf("%s\n", PQerrorMessage(conn));
        PQclear(res);

        res = PQexec(conn, "DELETE FROM test_table");
        if (!res)
                printf("%s\n", PQerrorMessage(conn));
        PQclear(res);

        PQfinish(conn);
}
```

```gcc -g --std=c11 -Wall -Wextra -I$(pg_config --includedir) test_pg.c -o test_pg -lpq```

```
import psycopg2 as pg
conn = pg.connect("dbname='gridka_db' user='gridka01' host='localhost' password='asdf1234'")

cur = conn.cursor()

cur.execute("CREATE TABLE test_table ( first_name VARCHAR, last_name VARCHAR )")

cur.execute("INSERT INTO test_table VALUES ( 'Vincent', 'Vega' )")
conn.commit()

cur.execute("SELECT * FROM test_table")
cur.fetchall()

cur.execute("INSERT INTO test_table (last_name, first_name) VALUES ( 'Jules', 'Winnfield' )")
conn.commit()

cur.execute("SELECT * FROM test_table")
print cur.fetchall()

cur.execute("DROP TABLE test_table")
conn.commit()
```

## MonetDB

```
monetdbd create /tmp/gridka_schema
monetdbd start /tmp/gridka_schema
monetdb create gridka_db
monetdb release gridka_db
```

```mclient -u monetdb -d gridka_db```   (default password: ```monetdb```)

```
CREATE USER "gridka01" WITH PASSWORD 'asdf1234' NAME 'gridka01' SCHEMA "sys";
CREATE SCHEMA "gridka01" AUTHORIZATION "gridka01";
ALTER USER "gridka01" SET SCHEMA "gridka01";
```

```
CREATE TABLE test_table ( first_name VARCHAR(64), last_name VARCHAR(64) );
INSERT INTO test_table VALUES ('Vincent', 'Vega');
INSERT INTO test_table (last_name, first_name) VALUES ('Jules', 'Winnfield');
SELECT * FROM test_table;
DELETE FROM test_table;
DROP test_table;
```

```
#include <stdio.h>
#include <stdlib.h>

#include <mapi.h>

int main()
{
        Mapi db;
        db = mapi_connect("localhost", 50000,
                          "gridka01", "asdf1234",
                          "sql", "gridka_db");
        if (mapi_error(db))
                mapi_explain(db, stderr);

        MapiHdl res;
        res = mapi_query(db, "CREATE TABLE test_table ( first_name VARCHAR(64), last_name VARCHAR(64) )");
        if (mapi_error(db))
                mapi_explain(db, stderr);
        mapi_close_handle(res);

        res = mapi_query(db, "INSERT INTO test_table VALUES ( 'Vincent', 'Vega' )");
        if (mapi_error(db))
                mapi_explain(db, stderr);
        mapi_close_handle(res);

        res = mapi_query(db, "INSERT INTO test_table (last_name, first_name) VALUES ( 'Jules', 'Winnfield' )");
        if (mapi_error(db))
                mapi_explain(db, stderr);
        mapi_close_handle(res);

        res = mapi_query(db, "SELECT * FROM test_table");
        if (mapi_error(db))
                mapi_explain(db, stderr);
        while(mapi_fetch_row(res)) {
                printf("%s %s\n", mapi_fetch_field(res, 0), mapi_fetch_field(res, 1));
        }
        mapi_close_handle(res);

        res = mapi_query(db, "DELETE FROM test_table");
        if (mapi_error(db))
                mapi_explain(db, stderr);
        mapi_close_handle(res);

        mapi_destroy(db);
}
```

```gcc -g -std=c11 -Wall -Wextra monetdb_test.c $(pkg-config --cflags --libs monetdb-mapi) -o monetdb_test```

```
import monetdb.sql as mo
conn = mo.connect(database='gridka_db', username='gridka01', hostname='localhost', password='asdf1234')

cur = conn.cursor()

cur.execute("CREATE TABLE test_table ( first_name VARCHAR(64), last_name VARCHAR(64) )")

cur.execute("INSERT INTO test_table VALUES ( 'Vincent', 'Vega' )")
conn.commit()

cur.execute("SELECT * FROM test_table")
cur.fetchall()

cur.execute("INSERT INTO test_table (last_name, first_name) VALUES ( 'Jules', 'Winnfield' )")
conn.commit()

cur.execute("SELECT * FROM test_table")
cur.fetchall()

cur.execute("DROP TABLE test_table")
conn.commit()
```

## LevelDB

```
mkdir gridka_db
```

```
#include <iostream>
#include <string>

#include <leveldb/db.h>

int main()
{
        leveldb::DB* db;
        leveldb::Options opts;
        leveldb::ReadOptions ropts;
        leveldb::WriteOptions wopts;
        leveldb::Status status;
        leveldb::Iterator* it;

        opts.create_if_missing = true;

        status = leveldb::DB::Open(opts, "gridka_db/test_table", &db);

        status = db->Put(wopts, "0", "{\"first_name\": \"Vincent\", \"last_name\": \"Vega\"}");
        status = db->Put(wopts, "1", "{\"first_name\": \"Jules\", \"last_name\": \"Winnfield\"}");

	    std::string value;
        db->Get(ropts, std::string("0"), &value);
		std::cout << value << '\n';

        it = db->NewIterator(ropts);
        for(it->SeekToFirst(); it->Valid(); it->Next())
                std::cout << it->key().ToString() << '\t' << it->value().ToString() << '\n';
        delete it;

        status = db->Delete(wopts, "0");
        status = db->Delete(wopts, "1");

        delete db;
}
```

```g++ -g -std=c++14 -Wall -Wextra leveldb_test.cpp -o leveldb_test -lleveldb```

```
import json
import leveldb
db = leveldb.LevelDB('gridka_db/test_table')
db.Put('0', json.dumps({'first_name': 'Vincent', 'last_name': 'Vega'}))
db.Put('1', json.dumps({'first_name': 'Jules', 'last_name': 'Winnfield'}))
json.loads(db.Get('0'))
it = db.RangeIter()
print [(x[0],json.loads(x[1])) for x in it]
db.Delete('0')
db.Delete('1')
```

## Redis

```vim /etc/redis/redis.conf```

```
requirepass asdf1234
```

```service redis restart```


```redis-cli```

```
auth asdf1234

set test_table:0 '{"first_name": "Vincent", "last_name": "Vega"}'
set test_table:1 '{"first_name": "Jules", "last_name": "Winnfield"}'

get test_table:0

hset mtest_table:0 first_name Vincent
hset mtest_table:0 last_name Vega
hset mtest_table:1 first_name Jules
hset mtest_table:1 last_name Winnfield

hget mtest_table:0 first_name
hget mtest_table:1 last_name

del test_table:0
del test_table:1
del mtest_table:0
del mtest_table:1
```

```
#include <stdio.h>
#include <stdlib.h>

#include <hiredis.h>

int main()
{
        redisContext *ctx;
        redisReply *r;

        ctx = redisConnect("localhost", 6379);
        if (ctx->err)
                printf("error: %s\n", ctx->errstr);

        r = redisCommand(ctx, "auth asdf1234");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hset mtest_table:0 first_name Vincent");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hset mtest_table:0 last_name Vega");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hset mtest_table:1 first_name Jules");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hset mtest_table:1 last_name Winnfield");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hget mtest_table:0 first_name");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        else
                printf("%s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "hget mtest_table:1 last_name");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        else
                printf("%s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "del mtest_table:0");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        r = redisCommand(ctx, "del mtest_table:1");
        if (r->type == REDIS_REPLY_ERROR)
                printf("error: %s\n", r->str);
        freeReplyObject(r);

        redisFree(ctx);
}
```

```gcc -g -std=c11 -Wall -Wextra redis_test.c -o redis_test $(pkg-config --cflags --libs hiredis)```

```
import redis
db = redis.StrictRedis(password='asdf1234')

db.set('test_table:0', '{"first_name": "Vincent", "last_name": "Vega"}')
db.set('test_table:1', '{"first_name": "Jules", "last_name": "Winnfield"}')

db.hset('mtest_table:0', 'first_name', 'Vincent')
db.hset('mtest_table:0', 'last_name', 'Vega')
db.hset('mtest_table:1', 'first_name', 'Jules')
db.hset('mtest_table:1', 'last_name', 'Winnfield')

db.delete('test_table:0')
db.delete('test_table:1')
db.delete('mtest_table:0')
db.delete('mtest_table:1')
```

## MongoDB

```
semanage port -a -t mongod_port_t -p tcp 27017
systemclt restart mongod
chkconfig mongod on
```

```mongo```

```
show dbs
use admin
db.createUser({"user": "admin", "pwd": "admin", "roles": ["userAdminAnyDatabase"]})
use gridka_db
show collections
db.createUser({"user": "gridka01", "pwd": "asdf1234", "roles": ["readWrite"]})
```

```vim /etc/mongod.conf```

```
auth=true
```

```service mongod restart```

```mongo gridka_db```

```
db.test_table.insert({"first_name": "Vincent", "last_name": "Vega"})
mongo -u gridka01 -p asdf1234 gridka_db
db.test_table.insert({"first_name": "Vincent", "last_name": "Vega"})
db.test_table.insert({"first_name": "Jules", "last_name": "Winnfield"})
db.test_table.find()
db.test_table.insert({"you_can_put": "whatever you want"})
db.test_table.find()
db.test_table.drop()
```

```
#include <stdio.h>
#include <stdlib.h>

#include <bson.h>
#include <mongoc.h>

int main ()
{
        mongoc_client_t *client;
        mongoc_collection_t *collection;
        bson_error_t error;
        bson_t *doc;
        bson_t *query;
        mongoc_cursor_t *cursor;
        char *str;

        mongoc_init();

        client = mongoc_client_new("mongodb://gridka01:asdf1234@localhost:27017/?authSource=gridka_db");
        collection = mongoc_client_get_collection (client,
                                                   "gridka_db",
                                                   "test_table");

        doc = BCON_NEW("first_name",BCON_UTF8("Vincent"),
                       "last_name", BCON_UTF8("Vega"));
        if(!mongoc_collection_insert(collection, MONGOC_INSERT_NONE,
                                     doc, NULL, &error))
                printf("error: %s\n", error.message);
        bson_destroy(doc);
        doc = BCON_NEW("first_name", BCON_UTF8("Jules"),
                       "last_name", BCON_UTF8("Winnfield"));
        if(!mongoc_collection_insert(collection, MONGOC_INSERT_NONE,
                                     doc, NULL, &error))
                printf("error: %s\n", error.message);
        bson_destroy(doc);

        query = bson_new();
        cursor = mongoc_collection_find(collection, MONGOC_QUERY_NONE,
                                        0, 0, 0, query, NULL, NULL);
        while(mongoc_cursor_next(cursor, &doc)) {
                str = bson_as_json(doc, NULL);
                printf("%s\n", str);
                bson_free(str);
        }
        bson_destroy(query);
        mongoc_cursor_destroy(cursor);

        if(!mongoc_collection_drop(collection, &error))
                printf("error: %s\n", error.message);

        mongoc_collection_destroy(collection);
        mongoc_client_destroy(client);
}
```

```gcc -g -std=c11 -Wall -Wextra mongo_test.c $(pkg-config --cflags --libs libmongoc-1.0) -o mongo_test```

```
from pymongo import MongoClient
client = MongoClient('mongodb://gridka01:asdf1234@localhost:27017/?authSource=gridka_db')
db = client.gridka_db
db.test_table.insert_one({'first_name': 'Vincent', 'last_name': 'Vega'})
db.test_table.insert_one({'first_name': 'Jules', 'last_name': 'Winnfield'})
[x for x in db.test_table.find()]
db.test_table.insert({'first_name': 'Marcellus', 'occupation': 'businessman'})
[x for x in db.test_table.find()]
db.test_table.drop()
```

## ElasticSearch

```curl localhost:9200```

```
import json, pprint
import elasticsearch
es = elasticsearch.Elasticsearch()

es.index(index='gridka_db', doc_type='person', id=0, body=json.dumps({'name': 'Vincent Vega', 'occupation': 'professional hitman'}))
pprint.pprint(es.search(index='gridka_db'))

es.index(index='gridka_db', doc_type='person', id=0, body=json.dumps({'age': 42}))
pprint.pprint(es.search(index='gridka_db'))

es.index(index='gridka_db', doc_type='person', id=0, body=json.dumps({'name': 'Vincent Vega', 'occupation': 'professional hitman', 'age': 42}))
pprint.pprint(es.search(index='gridka_db'))

es.index(index='gridka_db', doc_type='person', id=1, body=json.dumps({'name': 'Jules Winnfield', 'occupation': 'professional hitman', 'hidden_occupation': 'Director of SHIELD', 'age': 57}))
pprint.pprint(es.search(index='gridka_db'))

pprint.pprint(es.search(index='gridka_db', q='professional'))

pprint.pprint(es.search(index='gridka_db', q='occupation:professional'))

pprint.pprint(es.search(index='gridka_db', q='age:<50'))

es.index(index='gridka_db', doc_type='person', body=json.dumps({'name': 'Marcellus Wallace', 'occupation': 'businessman', 'age': 66}))

pprint.pprint(es.search(index='gridka_db', q='NOT occupation:hitman'))

pprint.pprint(es.search(index='gridka_db', q='NOT occupation:hitman AND NOT _type:misc'))

from elasticsearch.helpers import scan

scan(es, query={'query': {'match_all': {}}}, index='gridka_db', doc_type='person')

pprint.pprint([res for res in scan(es, query={'query': {'match_all': {}}}, index='gridka_db', doc_type='person')])

#es.delete(index='gridka_db', doc_type='person', id=u'AVbkQFrUfoCJqKB6H6bu')

#es.indices.delete(index='gridka_db')
```

## neo4j

Edit ```vim /etc/neo4j/neo4j.conf``` and uncomment ```dbms.connectors.default_listen_address=0.0.0.0```

Delete if exists ```rm /var/lib/neo4j/data/dbms/auth``` to reset the admin password.

Afterwards ```service neo4j restart```.


```http://localhost:7474/browser/```

```
CREATE (id_0:pulp_fiction {first_name: 'Vincent', last_name: 'Vega'})
CREATE (id_1:pulp_fiction {first_name: 'Jules', last_name: 'Winnfield'})
CREATE (id_0)-[:TELLS_STORY {about: 'le big mac'}]->(id_1)
CREATE (id_1)-[:TELLS_STORY {about: 'foot massage'}]->(id_0)

MATCH (n) RETURN (n)
MATCH (n) OPTIONAL MATCH (n)-[r]->() DELETE n,r

MATCH (n) DETACH DELETE (n)

CREATE (id_2:killbill {first_name: 'Beatrice', last_name: 'Kiddo'})

CREATE (id_2)-[:SAME_MOVE_UNIVERSE {about: 'tarantino'}]->(id_0)
CREATE (id_2)-[:SAME_MOVE_UNIVERSE {about: 'tarantino'}]->(id_1)

MATCH (n) where ID(n) in [11,12,13] DETACH DELETE(n)

MATCH (a) WHERE ID(a)=18 MATCH(b) WHERE ID(b)=16 MERGE (a)-[:SAME_MOVE_UNIVERSE {about: 'tarantino'}]-(b)
MATCH (a) WHERE ID(a)=18 MATCH(b) WHERE ID(b)=17 MERGE (a)-[:SAME_MOVE_UNIVERSE {about: 'tarantino'}]-(b)
```

```
import pprint
from py2neo import Graph, Node, Relationship

graph = Graph("http://localhost:7474/db/data/")

id_0 = Node("pulp_fiction", first_name='Vincent', last_name='Vega')
id_1 = Node("pulp_fiction", first_name='Jules', last_name='Winnfield')
graph.create(id_0)
graph.create(id_1)
graph.create(Relationship(id_0, 'TELLS_STORY', id_1, about='le big mac'))
graph.create(Relationship(id_1, 'TELLS_STORY', id_0, about='foot massage'))
pprint.pprint([node for node in graph.match()])
```
