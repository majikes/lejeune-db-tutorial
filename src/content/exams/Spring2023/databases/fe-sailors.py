#!/usr/bin/env python
''' Create sailors for the final exam'''
# pylint: disable=line-too-long, invalid-name, redefined-outer-name
from datetime import date, timedelta
import json
import os
import re
import sqlite3

import numpy as np

SailorNames = "Albert Dustin Brutus Lubber Andy Rusty Horatio Zorba Art Bob Frodo Homer Bart Lisa Marge Majikes".split()
SailorIds = [100+i for i in range(len(SailorNames))]
SailorAges = np.random.choice(np.arange(16,65), len(SailorNames), True)
SailorRatings = np.random.choice(10, len(SailorNames), True)
NBoats = 19
BoatIds = [100 + i for i in range(NBoats)]
BoatColors = "red green blue".split()
BoatColors = np.random.choice(BoatColors, NBoats, True)
BoatNames = np.random.choice("Interlake Clipper Sunfish Marine".split(), NBoats, True)
NDates = 40
Years = np.random.choice(np.arange(2012,2015), NDates, True)
Months = np.random.choice(np.arange(5,9), NDates, True)
Days = np.random.choice(np.arange(1, 32), NDates, True)
Dates = [ f'{Years[i]:4}-{Months[i]:2}-{Days[i]:2}' for i in range(NDates)]
NReserves = 60
RSid = np.random.choice(SailorIds, NReserves, True)
RBid = np.random.choice(BoatIds, NReserves, True)
RDate = np.random.choice(Dates, NReserves, True)




fn1 = 'fe-sailors-1.sqlite'
fn2 = 'fe-sailors-2.sqlite'
conns = []
cursors = []
for fn in [fn1, fn2]:
    if os.path.isfile(fn):
        os.remove(fn)
    conn = sqlite3.connect(fn)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    conns.append(conn)
    cursors.append(cursor)

    # Sailors table
    cursor.execute("""CREATE TABLE Sailors (sid INTEGER PRIMARY KEY,
                                            sname TEXT,
                                            rating INTEGER,
                                            age INTEGER) """)
    for index, SailorName in enumerate(SailorNames):
        cursor.execute("""INSERT INTO Sailors (sid, sname, rating, age)
                                      VALUES (:sid, :sname, :rating, :age)""",
                       dict(sid=int(SailorIds[index]), sname=SailorName,
                            rating=int(SailorRatings[index]), age=int(SailorAges[index])))

    # Boats
    cursor.execute("""CREATE TABLE Boats (bid INTEGER PRIMARY KEY,
                                          bname TEXT,
                                          color TEXT)""")
    for index, BoatName in enumerate(BoatNames):
        cursor.execute("""INSERT INTO Boats ( bid,  bname,  color)
                                      VALUES(:bid, :bname, :color)""",
                       dict(bid=int(BoatIds[index]), bname=BoatName, color=BoatColors[index]))

    # Reserves
    cursor.execute("""CREATE TABLE Reserves (sid INTEGER,
                                             bid INTEGER,
                                             day TEXT, -- yyyy-mm-dd
                                             FOREIGN KEY (sid) REFERENCES Sailors(sid)
                                                 ON DELETE CASCADE
                                             FOREIGN KEY (bid) REFERENCES Boats(bid)
                                                 ON DELETE CASCADE)""")
    for index, day in enumerate(RDate):
        corrected_date = day.replace(' ', '0')
        cursor.execute("""INSERT INTO Reserves (sid, bid, day)
                                      VALUES (:sid, :bid, :day)""",
                       dict(sid=int(RSid[index]), bid=int(RBid[index]),
                            day=corrected_date))
    conn.commit()

def ensureReservedAllBoats(cursor, name):  # pylint: disable=redefined-outer-name
    '''Ensure this sailor reserved all boats'''
    cursor.execute(''' SELECT sid FROM Sailors where sname=:name ''',
                   dict(name=name))
    sid = cursor.fetchone()[0]

    cursor.execute('''SELECT bid
                        FROM Boats
                       WHERE bid NOT IN (SELECT bid
                                           FROM Reserves
                                          WHERE sid=:sid )''',
                   dict(sid=sid))
    for row in cursor.fetchall():
        bdate = date(2013, 1, 1) + timedelta(days=int(row['bid']))
        cursor.execute('''INSERT INTO Reserves ( sid,  bid,  day)
                                        Values (:sid, :bid, :day)''',
                       dict(sid=sid, bid=row['bid'], day=bdate.strftime("%Y-%m-%d")))
    cursor.connection.commit()

def ensureReservedAllLakeBoats(cursor, name):  # pylint: disable=redefined-outer-name
    '''Ensure this sailor reserved all boats with lake in its name'''
    cursor.execute('''SELECT sid FROM Sailors where sname=:name ''',
                   dict(name=name))
    sid = cursor.fetchone()[0]

    cursor.execute('''SELECT B.bid
                        FROM Boats B
                       WHERE B.bname LIKE '%lake%' AND
                             B.bid not in (SELECT R.bid
                                             FROM Reserves R
                                            WHERE R.sid=:sid)''',
                   dict(sid=sid))
    for row in cursor.fetchall():
        bdate = date(2012, 1, 1) + timedelta(days=int(row['bid']))
        cursor.execute('''INSERT INTO Reserves (sid, bid, day)
                                        Values (:sid, :bid, :day)''',
                       dict(sid=sid, bid=row['bid'], day=bdate.strftime("%Y-%m-%d")))
    cursor.connection.commit()

# Ensure Majikes not in the second sailors
cursor.execute('''DELETE FROM Reserves where sid=(SELECT sid from Sailors where sname='Majikes')''')
conn.commit()

# Add a boat CV-6 USS Enterprise
cursors[1].execute("""INSERT INTO Boats ( bid,  bname,  color)
                                 VALUES(6, 'USS Enterprise', 'gray')""")
cursors[1].execute("""INSERT INTO Sailors (sid, sname, rating, age)
                                   VALUES (5572, 'Admiral Chester W. Nimitz', 10, 117)""")
cursors[1].execute("""INSERT INTO Reserves(sid, bid, day)
                                   VALUES (5572, 6, '1942-06-04')""")
cursors[1].connection.commit()

# Ensure all sailors used in question Last.Reserved.Boat reserved some boats more than once
for index,sname in enumerate(['Albert', 'Lubber', 'Brutus', 'Dustin']):
    cursors[1].execute(f'''SELECT sid FROM Sailors where sname='{sname}' ''')
    sid = cursors[1].fetchone()['sid']
    cursors[1].execute(f'''INSERT INTO Reserves (sid, bid, day)
                                   VALUES({sid}, {100+index}, '2023-0{index+2}-0{index+1}')  ''')
    cursors[1].execute(f'''INSERT INTO Reserves (sid, bid, day)
                                   VALUES({sid}, {100+index}, '2023-0{index+1}-0{index+1}')  ''')
cursors[1].connection.commit()

# Ensure all that one boat of each name has been reserved all the sailors
for bname in ['Interlake', 'Clipper', 'Sunfish', 'Marine']:
    assert bname in BoatNames
    cursors[1].execute('''SELECT bid
                            FROM Boats
                           WHERE bname = :bname''',
                       dict(bname=bname))
    bid = cursor.fetchone()['bid']
    cursors[1].execute('''SELECT sid
                            FROM Sailors
                           WHERE sid not in (SELECT sid
                                               FROM Reserves R
                                              WHERE R.bid=:bid)''',
                       dict(bid=bid))
    sids = [x['sid'] for x in cursor.fetchall()]
    for index,sid in enumerate(sids):
        cursors[1].execute('''INSERT INTO Reserves (bid, sid, day)
                                           VALUES(:bid, :sid, :day)''',
                          dict(bid=bid, sid=sid,
                               day=f'2022-{(index%12)+1:02d}-{index+1:02d}'))
cursors[1].connection.commit()

for index,sname in enumerate(['Albert', 'Lubber', 'Brutus', 'Dustin']):
    cursors[1].execute(f'''SELECT sid FROM Sailors where sname='{sname}' ''')
    sid = cursors[1].fetchone()['sid']
    cursors[1].execute(f'''INSERT INTO Reserves (sid, bid, day)
                                   VALUES({sid}, {100+index}, '2023-0{index+2}-0{index+1}')  ''')
    cursors[1].execute(f'''INSERT INTO Reserves (sid, bid, day)
                                   VALUES({sid}, {100+index}, '2023-0{index+1}-0{index+1}')  ''')
cursors[1].connection.commit()

# Change Frodo's sid
cursors[1].execute("SELECT sid FROM Sailors where sname='Frodo'")
old_sid = cursor.fetchone()[0]
cursors[1].execute("SELECT max(sid) FROM Sailors where sid!=5572")
new_sid = cursor.fetchone()[0] + 1
cursors[1].execute('PRAGMA foreign_keys = OFF')
cursors[1].execute("UPDATE Sailors set sid=:new_sid WHERE sid=:old_sid",
                  dict(new_sid=new_sid, old_sid=old_sid))
cursors[1].execute('PRAGMA foreign_keys = ON')
cursors[1].execute("UPDATE Reserves set sid=:new_sid WHERE sid=:old_sid",
                  dict(new_sid=new_sid, old_sid=old_sid))
cursors[1].connection.commit()

cursor.execute('''SELECT sql
                    FROM sqlite_schema
                   WHERE type='table' ''')
schema = re.sub("\n  *",
                "\n     ",
                "\n".join([x[0] for x in cursor.fetchall()]))
schema = re.sub(r'CREATE TABLE sqlite_sequence\(name,seq\)\n', '', schema)
with open(fn1.replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
    json.dump(schema, fid)
