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

databases = ['game-sailors-1.sqlite', 'game-sailors-2.sqlite']

for database in databases:
    if os.path.exists(database):
        os.remove(database)
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    conn.cursor().execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()

    cursor.execute("""
          CREATE TABLE Sailors
              (sid INTEGER PRIMARY KEY,
               sname TEXT,
               rating INTEGER,
               age INTEGER)
                   """)
    for i,sailor in enumerate(SailorNames):
        cursor.execute("""
              INSERT INTO Sailors (sid, sname, rating, age)
                           VALUES (:sid, :sname, :rating, :age)  """,
                       dict(sid=int(SailorIds[i]),
                            sname=sailor,
                            rating=int(SailorRatings[i]),
                            age=int(SailorAges[i])))

    cursor.execute("""
        CREATE TABLE Boats
        (bid INTEGER PRIMARY KEY,
         bname TEXT,
         color TEXT)
                   """)
    for i in range(NBoats):
        cursor.execute("""
              INSERT INTO Boats (bid, bname, color)
                          VALUES (:bid, :bname, :color)
                          """,
                       dict(bid=int(BoatIds[i]),
                            bname=BoatNames[i],
                            color=BoatColors[i]))

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
            cursor.execute("""
                  INSERT INTO Reserves (sid, bid, day)
                                VALUES (:sid, :bid, :day)
                                """,
                           dict(sid=int(RSid[i]),
                                bid=int(RBid[i]),
                                day=RDate[i]))
        except sqlite3.IntegrityError:
            # print(f'Inserting i={i} sid {RSid[i]} bid {RBid[i]} day {RDate[i]}: {e}')
            # print('Ingnoring reservation')
            pass

    conn.commit()

# Make the two databases different
cursor.execute("""
      INSERT INTO Sailors (sid, sname, rating, age)
                   VALUES (:sid, :sname, :rating, :age)  """,
               dict(sid=len(SailorNames)+101,
                    sname='Majikes',
                    rating=np.random.choice(10, 1, True)[0],
                    age=62))
cursor.execute("""
      INSERT INTO Reserves (sid, bid, day)
                   VALUES (:sid, :bid, :day)  """,
               dict(sid=len(SailorNames)+101,
                    bid=111,
                    day='2016-04-16'))
cursor.execute(""" SELECT sid FROM Sailors where sname='Albert' """)
sid = cursor.fetchone()['sid']
cursor.execute("""
      INSERT INTO Reserves (sid, bid, day)
                   VALUES (:sid, :bid, :day)  """,
               dict(sid=sid,
                    bid=111,
                    day='2016-04-16'))

# Make Bart reserve all boats
cursor.execute(""" SELECT sid FROM Sailors where sname='Bart' """)
sid = cursor.fetchone()['sid']

cursor.execute(""" SELECT bid FROM Boats
                     WHERE bid NOT IN (SELECT bid from Reserves where sid=:sid)  """,
               dict(sid=sid))
for row in cursor.fetchall():
    cursor.execute(f"""INSERT INTO Reserves (sid, bid, day)
                                     Values (:sid, :bid, '2013-12-{str(row["bid"])[-2:]}')   """,
                   dict(sid=sid, bid=row['bid']))
conn.commit()

# Make Marge reserve all boats with Lake
cursor.execute(''' SELECT sid FROM Sailors where sname='Lisa' ''')
sid = cursor.fetchone()['sid']

cursor.execute("""SELECT B.bid
                    FROM Boats B
                   WHERE B.bname LIKE '%lake%' AND
                         B.bid NOT IN (SELECT R.bid
                                         FROM Reserves R
                                        WHERE R.sid=:sid)   """,
               dict(sid=sid))
for row in cursor.fetchall():
    cursor.execute(f"""INSERT INTO Reserves (sid, bid, day)
                                     VALUES (:sid, :bid, '2014-12-{str(row["bid"])[-2:]}') """,
                   dict(sid=sid, bid=row['bid']))
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
