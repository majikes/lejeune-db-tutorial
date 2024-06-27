#!/usr/bin/env python
""" Create Sailors.sqlqite """

# pylint: disable=line-too-long,invalid-name

import json
import os
import re
import sqlite3
from contextlib import closing

import numpy as np

SailorNames = "Albert Dustin Brutus Lubber Andy Rusty Horatio Zorba Art Bob Frodo Homer Bart Lisa Marge".split()
SailorIds = [100+i for i in range(len(SailorNames))]
SailorAges = np.random.choice(np.arange(16,65), len(SailorNames), True)
SailorRatings = np.random.choice(10, len(SailorNames), True)
NBoats = 19
BoatIds = [100 + i for i in range(NBoats)]
BoatColors = "red green blue".split()
BoatColors = np.random.choice(BoatColors, NBoats, True)
BoatNames = np.random.choice("Interlake Clipper Marine".split(), NBoats, True)
NDates = 40
Years = np.random.choice(np.arange(2012,2015), NDates, True)
Months = np.random.choice(np.arange(5,9), NDates, True)
Days = np.random.choice(np.arange(1, 32), NDates, True)
Dates = [ f'{Years[i]:04}-{Months[i]:02}-{Days[i]:01}' for i in range(NDates)]
NReserves = 60
RSid = np.random.choice(SailorIds, NReserves, True)
RBid = np.random.choice(BoatIds, NReserves, True)
RDate = np.random.choice(Dates, NReserves, True)

databases = ['wkst-ch5-sailors-1.sqlite', 'wkst-ch5-sailors-2.sqlite']

for database in databases:
    if os.path.exists(database):
        os.remove(database)
    conn = sqlite3.connect(database)
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE Sailors
        (sid INTEGER PRIMARY KEY,
         sname TEXT,
         rating INTEGER,
         age INTEGER)
    """)

    for i,sailor in enumerate(SailorNames):
        cursor.execute("INSERT INTO Sailors (sid, sname, rating, age) values(?, ?, ?, ?)",
                       (int(SailorIds[i]), sailor, int(SailorRatings[i]), int(SailorAges[i])))

    cursor.execute("""
    create table Boats
            (bid INTEGER PRIMARY KEY,
             bname TEXT,
             color TEXT)
        """)

    for i in range(NBoats):
        cursor.execute("insert into Boats (bid, bname, color) values (?, ?, ?)",
                       (int(BoatIds[i]), BoatNames[i], BoatColors[i]))

    cursor.execute("""
        CREATE TABLE Reserves
            (sid INTEGER,
             bid INTEGER,
             day TEXT,
             PRIMARY KEY (sid, day)
             FOREIGN KEY (sid) REFERENCES Sailors(sid)
             FOREIGN KEY (bid) REFERENCES Boats(bid))
        """)

    for i in range(NReserves):
        try:
            cursor.execute("insert into Reserves (sid, bid, day) VALUES(?, ?, ?)",
                           (int(RSid[i]), int(RBid[i]), RDate[i]))
        except sqlite3.IntegrityError:
            pass

    conn.commit()

# Question 1  add a duplicate reserve for boat 103
cursor.execute(''' SELECT sid, bid, day from Reserves where bid=103''')
sid, bid, day = cursor.fetchone()
day = f'2023-{day[5:]}'
cursor.execute(''' INSERT INTO Reserves (sid, bid, day)
                                  VALUES(:sid, :bid, :day)''',
               dict(sid=sid, bid=bid, day=day))

# Make Lisa reserve all boats in databases[1]
cursor.execute(''' SELECT sid FROM Sailors where sname='Lisa' ''')
sid = cursor.fetchone()[0]

cursor.execute(''' SELECT bid FROM Boats
                     WHERE bid NOT IN (SELECT bid from Reserves where sid= ? )''',
               (sid, ))
bids = [ x[0] for x in cursor ]

for bid in bids:
    cursor.execute(f'''INSERT INTO Reserves (sid, bid, day)
                        Values( ?, ?, '2013-12-{str(bid)[-2:]}')''',
                            (sid, bid))
conn.commit()

# Make Marge reserve all boats with Lake
cursor.execute(''' SELECT sid FROM Sailors where sname='Marge' ''')
sid = cursor.fetchone()[0]

cursor.execute('''SELECT B.bid
                    FROM Boats B
                   WHERE B.bname LIKE '%lake%' AND
                         B.bid NOT IN (SELECT R.bid
                                         FROM Reserves R
                                        WHERE R.sid=?)''',
               (sid,))
bids = [ x[0] for x in cursor ]

for bid in bids:
    cursor.execute(f'''INSERT INTO Reserves (sid, bid, day)
                        Values( ?, ?, '2014-12-{str(bid)[-2:]}')''',
                            (sid, bid))
conn.commit()

# Get the schema
with closing(conn.cursor()) as cursor:
    cursor.execute('''SELECT sql
                        FROM sqlite_schema
                       WHERE type='table'  ''')
    schema = re.sub("\n  *",
                    "\n     ",
                    "\n".join([x[0] for x in cursor.fetchall()]))

with open(database.replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
    json.dump(schema, fid)
