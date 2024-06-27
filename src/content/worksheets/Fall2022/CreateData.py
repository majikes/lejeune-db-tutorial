#!/usr/bin/env python

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
Dates = [ '%4d-%02d-%02d' % (Years[i], Months[i], Days[i]) for i in range(NDates)]
NReserves = 60
RSid = np.random.choice(SailorIds, NReserves, True)
RBid = np.random.choice(BoatIds, NReserves, True)
RDate = np.random.choice(Dates, NReserves, True)



import sqlite3

conn = sqlite3.connect('sailors.sqlite')
cursor = conn.cursor()

# setup tables
cursor.executescript("""
    drop table if exists Sailors;
    drop table if exists Boats;
    drop table if exists Reserves;
""")

cursor.execute("""
create table Sailors
    (sid integer primary key, 
     sname text, 
     rating integer, 
     age integer)
""")

for i in range(len(SailorNames)):
    cursor.execute("insert into Sailors (sid, sname, rating, age) values(?, ?, ?, ?)", 
                   (int(SailorIds[i]), SailorNames[i], int(SailorRatings[i]), int(SailorAges[i])))

cursor.execute("""
create table Boats
    (bid integer primary key, 
     bname text, 
     color text)
""")

for i in range(NBoats):
    cursor.execute("insert into Boats values (?, ?, ?)", 
                   (int(BoatIds[i]), BoatNames[i], BoatColors[i]))

cursor.execute("""
create table Reserves 
    (sid integer, 
     bid integer, 
     day text, 
     primary key (sid, day) 
     foreign key (sid) references Sailors(sid)
     foreign key (bid) references Boats(bid))
""")

for i in range(NReserves):
    try:
        cursor.execute("insert into Reserves values(?, ?, ?)", 
                       (int(RSid[i]), int(RBid[i]), RDate[i]))
    except sqlite3.IntegrityError:
        pass
    
conn.commit()

# Make Lisa reserve all boats
cursor.execute(''' SELECT sid FROM Sailors where sname='Lisa' ''')
sid = cursor.fetchone()[0]

cursor.execute(''' SELECT bid FROM Boats
                     WHERE bid not in (SELECT bid from Reserves where sid= ? )''',
               (sid, ))
bids = [ x[0] for x in cursor ]

for bid in bids:
    cursor.execute(f'''INSERT INTO Reserves
                        Values( ?, ?, '2013-12-{str(bid)[-2:]}')''',
                            (sid, bid))
conn.commit()

# Make Marge reserve all boats with Lake
cursor.execute(''' SELECT sid FROM Sailors where sname='Marge' ''')
sid = cursor.fetchone()[0]

cursor.execute('''SELECT B.bid
                    FROM Boats B 
                   WHERE B.bname LIKE '%lake%' AND
                         B.bid not in (SELECT R.bid
                                         FROM Reserves R
                                        WHERE R.sid=?)''',
               (sid,))
bids = [ x[0] for x in cursor ]

for bid in bids:
    cursor.execute(f'''INSERT INTO Reserves
                        Values( ?, ?, '2014-12-{str(bid)[-2:]}')''',
                            (sid, bid))
conn.commit()
