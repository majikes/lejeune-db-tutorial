#!/usr/bin/env python3
import csv
import os
import sqlite3
import yaml

fname1 = 'states-A.sqlite'
fname2 = 'states-B.sqlite'
fname_executives = 'executive.yaml'
fname_legislators_current = 'legislators-current.yaml'
fname_legislators_historical = 'legislators-historical.yaml'
fname_states = 'states_population.csv'

if os.path.isfile(fname1):
    os.remove(fname1)
if os.path.isfile(fname2):
    os.remove(fname2)

# States
states = []
with open(fname_states, encoding='utf-8') as csvfile:
   state_rdr = csv.reader(csvfile, delimiter=',')
   headers = next(state_rdr, None)
   headers = ['abbrev', 'state', 'population']  # Remove utf \ufeff
   for row in state_rdr:
      states.append(dict(abbrev=row[0], state=row[1], population=int(row[2])))

# Legislators
with open(fname_legislators_current, 'r') as stream:
    legislators = yaml.load(stream, Loader=yaml.SafeLoader)
with open(fname_legislators_historical, 'r') as stream:
    legislators_historical = yaml.load(stream, Loader=yaml.SafeLoader)
# Executives
with open(fname_executives, 'r') as stream:
    executives = yaml.load(stream, Loader=yaml.SafeLoader)

conn1 = sqlite3.connect(fname1)
c1 = conn1.cursor()
conn2 = sqlite3.connect(fname2)
c2 = conn2.cursor()

for c in [c1, c2]:
   c.execute('''
      CREATE TABLE IF NOT EXISTS States
         (abbrev char(2) PRIMARY KEY,
          statename char(20),
          population integer)''')
   c.execute('''
      CREATE TABLE IF NOT EXISTS Politicians
         (bioid char(20),
          firstname char(20),
          lastname char(20),
          birthday date,
          gender char(1),
          PRIMARY KEY(bioid))''')
   c.execute('''
      CREATE TABLE IF NOT EXISTS Terms
         (termid INTEGER PRIMARY KEY AUTOINCREMENT,
          termtype char(20),
          startdate date,
          enddate date,
          party char(20),
          how char(20),
          bioid char(20),
          district integer,
          state char(2),
          FOREIGN KEY(bioid) REFERENCES Politicians(bioid))''')

for s in states:
   for c in [c1, c2]:
      try:
         c.execute('''
            INSERT INTO States (abbrev, statename, population)
              VALUES(?, ?, ?)''',
               [s['abbrev'], s['state'], s['population']])
      except Exception as ex:
           import pdb; pdb.set_trace()
           print(ex, s)

for e in legislators + executives:
   bioid = e['id'].get('bioguide',
                       e['id'].get('govtrack',
                                   e['id'].get('icpsr_prez',
                                               e['id'].get('icpsr', None))))
   assert bioid
   gender = e['bio'].get('gender', 'M')
   assert gender in ['M', 'F']
   for c in [c1, c2]:
      c.execute('''
         INSERT INTO Politicians (bioid, firstname, lastname, birthday, gender)
              Values(?, ?, ?, ?, ?)''',
               [f"{bioid}", e['name']['first'], e['name']['last'],
                e['bio']['birthday'], gender])
      for t in e['terms']:
       try:
         how_elected = t.get('how', 'election')
         state = t.get('state', 'N/A')  # Can't handle Null
         district = t.get('district', -1)  # Can't handle Null
         c.execute('''
           INSERT INTO Terms (termtype, startdate, enddate, party, how, bioid, state, district)
                Values(?, ?, ?, ?, ?, ?, ?, ?)''',
                  [t['type'], t['start'], t['end'], t['party'], how_elected, bioid, state, district])
       except Exception as ex:
             print(ex, e, t)
             import pdb; pdb.set_trace()
             print('c1' if c == c1 else 'c2')

# all bioids
c1.execute('''SELECT DISTINCT bioid from Politicians''')
bioids = [ b[0] for b in c1.fetchall() ]
for l in legislators_historical:
   bioid = l['id'].get('bioguide',
                       l['id'].get('govtrack',
                                   l['id'].get('icpsr_prez',
                                               l['id'].get('icpsr', None))))
   if bioid in bioids:
      for t in l['terms']:
       try:
         how_elected = t.get('how', 'election')
         state = t.get('state', 'N/A')  # Can't handle Null
         district = t.get('district', -1)  # Can't handle Null
         party = t.get('party', 'no party')
         c.execute('''
           INSERT INTO Terms (termtype, startdate, enddate, party, how, bioid, state, district)
                Values(?, ?, ?, ?, ?, ?, ?, ?)''',
                  [t['type'], t['start'], t['end'], party, how_elected, bioid, state, district])
       except Exception as ex:
             print(ex, l, t)
             import pdb; pdb.set_trace()
             print('c1' if c == c1 else 'c2')


# Add terms

c1.execute('''DELETE FROM Politicians
               WHERE bioid in ('B000444', '412733', 'P000587', 'H001075')''')
c1.execute('''DELETE FROM States
               WHERE abbrev not in ('NH', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'N/A' )''')
c1.execute('''DELETE FROM Terms
               WHERE state not in ('NH', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA', 'DE', 'MD', 'VA', 'NC', 'SC', 'GA', 'N/A' )''')
c1.execute('''DELETE FROM Politicians
               WHERE birthday < '1900-00-00' or
                     bioid not in (Select bioid from Terms) ''')
for c in [c1, c2]:
    c.execute('''update Terms set State=Null where state='N/A' ''')
    c.execute('''update Terms set district=Null where district=-1''')

conn1.commit()
conn2.commit()
