# Hands-On Session 3

## Grab and prepare training data

Dataset from UCIML Kaggle Challenge.

```
wget https://raw.githubusercontent.com/mlassnig/Databases-Introductory-Course/master/data/pima-indians-diabetes.data
```

Attributes:

1. Number of times pregnant
2. Plasma glucose concentration a 2 hours in an oral glucose tolerance test
3. Diastolic blood pressure (mm Hg)
4. Triceps skin fold thickness (mm)
5. 2-Hour serum insulin (mu U/ml)
6. Body mass index (weight in kg/(height in m)^2)
7. Diabetes pedigree function
8. Age (years)
9. Class variable (0 or 1)


## Feed training data into PostgreSQL

```
create table ml (pregnant integer, plasma integer, diastolic integer, triceps integer, insulin integer, bmi float, pedigree float, age integer, class integer);
\copy ml from 'pima-indians-diabetes.data' with (format csv);
```

## Feed training data into ElasticSearch

```
from itertools import islice

import datetime

import elasticsearch
from elasticsearch import helpers

es = elasticsearch.Elasticsearch()


with open('datafile.csv') as f:
    while True:
        next_n_lines = list(islice(f, 10))
        if not next_n_lines:
            break

        print 'cycle'
        next_n_lines = [n.split(',') for n in next_n_lines]

        actions = [{'_index': 'ml', '_type': 'measurement', '_source': {'pregnant': int(n[0]),
		                                                                'plasma': n[1],
                                                                        'diastolic': n[2],
                                                                        'triceps': n[3],
                                                                        'insulin': n[4],
                                                                        'bmi': n[5],
                                                                        'pedigree': n[6],
                                                                        'age': n[7],
																		'triceps': n[8]}} for n in next_n_lines]

        helpers.bulk(es, actions)
```


## Run ML model on flat file

```
from keras.models import Sequential
from keras.layers import Dense

import numpy
numpy.random.seed(7)

dataset = numpy.loadtxt("pima-indians-diabetes.data", delimiter=",")
X = dataset[:,0:8]
Y = dataset[:,8]

model = Sequential()
model.add(Dense(12, input_dim=8, activation='relu'))
model.add(Dense(8, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(X, Y, epochs=150, batch_size=10)

scores = model.evaluate(X, Y)
print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))

predictions = model.predict(X)

rounded = [round(x[0]) for x in predictions]
print(rounded)
```

Cite: https://machinelearningmastery.com


## From PostgreSQL

Replace at appropriate point:

```
import psycopg2 as pg
cur = conn.cursor()
cur.execute("select * from ml")
dataset = numpy.array(cur.fetchall())
```

## From ElasticSearch

Replace at appropriate point:

```
import elasticsearch
es = elasticsearch.Elasticsearch()
dataset = numpy.array([[r['_source']['pregnant'], r['_source']['plasma'], r['_source']['diastolic'], r['_source']['triceps'], r['_source']['insulin'], r['_source']['bmi'], r['_source']['pedigree'], r['_source']['age']] for r in scan(es, query={'query': {'match_all': {}}}, index='ml', doc_type='measurement')])
```

## SQLAlchemy

```
sudo apt install python-sqlalchemy python-psycopg2
```

```
from sqlalchemy import create_engine
engine = create_engine('postgresql://gridka01:asdf1234@localhost:5432/gridka_db', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, DateTime, Enum, Integer, String, Index, ForeignKeyConstraint

import datetime

class MoralityType():
    GOOD = 'G'
    NEUTRAL = 'N'
    EVIL = 'E'

class Affiliation(Base):
    __tablename__ = 'affiliation'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    morality = Column(String(1))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args = (Index('IDX_AFFILIATION_CREATED', 'created_at'))

class Starship(Base):
    __tablename__ = 'starship'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    affiliation_id = Column(String(128), nullable=False)
    crew = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    __table_args = (Index('IDX_STARSHIP_CREATED', 'created_at'),
                    ForeignKeyConstraint(['affiliation_id'], ['affiliation.id'],
                                         name='FK_STARSHIP_AFFILIATION'))

Base.metadata.create_all(engine)


from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

session.add(Affiliation(name='Galactic Empire', morality=MoralityType.EVIL))
session.add(Affiliation(name='Starfleet', morality=MoralityType.GOOD))
session.add(Affiliation(name='Klingon', morality=MoralityType.NEUTRAL))


session.add(Starship(name='Enterprise', affiliation_id='2', crew=430))
session.add(Starship(name='Warbird', affiliation_id='3', crew=80))
session.add(Starship(name='TIE Fighter', affiliation_id='1', crew=1))


session.commit()


session.query(Affiliation).all()

session.query(Starship).all()
```
