#!/usr/bin/env python3
''' Create the politician databases '''
# pylint: disable=invalid-name, line-too-long
import json
import os
import re
import sqlite3
import warnings

import yaml
import pandas as pd

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning) # Don't care about pandas perf

fname1 = 'fe_politicians1.sqlite'
fname2 = 'fe_politicians2.sqlite'
# wget https://raw.githubusercontent.com/unitedstates/congress-legislators/master/executive.yaml
fname_executives = 'executive.yaml'
# 1MB wget https://raw.githubusercontent.com/unitedstates/congress-legislators/main/legislators-current.yaml
fname_legislators_current = 'legislators-current.yaml'
# wget https://raw.githubusercontent.com/unitedstates/congress-legislators/main/committees-historical.yaml
fname_legislators_historical = 'legislators-historical.yaml'

fname_states = 'states_population.csv'
# kaggle login https://www.kaggle.com/datasets/peretzcohen/2019-census-us-population-data-by-state?resource=download
fname_states = '2019_Census_US_Population_Data_By_State_Lat_Long.csv'
# us-state-capitals https://github.com/jasperdebie/VisInfo/blob/master/us-state-capitals.csv
# populations  https://www.census.gov/data/tables/time-series/demo/popest/2020s-state-total.html#par_textimage
# download populations https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/state/totals/NST-EST2021-alldata.csv
fname_states_capital = 'us-state-capitals.csv'
fname_states_population = 'NST-EST2021-alldata.csv'

term_type_dict = dict(prez='President', viceprez='Vice President', sen='Senator', rep='Representative')


if os.path.isfile(fname1):
    os.remove(fname1)
if os.path.isfile(fname2):
    os.remove(fname2)

# States
capital_df = pd.read_csv(fname_states_capital)
assert all(capital_df.columns == ['name', 'description', 'latitude', 'longitude'])
capital_df.columns = ['state_name', 'state_capital', 'capital_latitude', 'capital_longitude']
capital_df.set_index('state_name')

population_df = pd.read_csv(fname_states_population, usecols=['NAME', 'POPESTIMATE2021'])
population_df.columns = ['state_name', 'state_population']
population_df.set_index('state_name')

states_df = capital_df.merge(population_df)

with open(fname_legislators_current, 'r', encoding='utf-8') as f:
    legislators_current_df = pd.json_normalize(yaml.safe_load(f))
assert all(legislators_current_df.columns == ['terms', 'id.bioguide', 'id.thomas', 'id.lis', 'id.govtrack', 'id.opensecrets', 'id.votesmart', 'id.fec', 'id.cspan', 'id.wikipedia', 'id.house_history', 'id.ballotpedia', 'id.maplight', 'id.icpsr', 'id.wikidata', 'id.google_entity_id', 'name.first', 'name.last', 'name.official_full', 'bio.birthday', 'bio.gender', 'name.middle', 'name.nickname', 'name.suffix', 'leadership_roles', 'other_names', 'family'])

with open(fname_legislators_historical, 'r', encoding='utf-8') as f:
    legislators_historical_df = pd.json_normalize(yaml.safe_load(f))
assert all(legislators_historical_df.columns == ['terms', 'id.bioguide', 'id.govtrack', 'id.icpsr', 'id.wikipedia', 'id.wikidata', 'id.google_entity_id', 'name.first', 'name.last', 'bio.birthday', 'bio.gender', 'id.house_history', 'name.middle', 'name.nickname', 'id.ballotpedia', 'name.suffix', 'id.bioguide_previous', 'id.house_history_alternate', 'other_names', 'id.thomas', 'id.cspan', 'id.votesmart', 'id.lis', 'name.official_full', 'id.opensecrets', 'id.fec', 'id.maplight', 'leadership_roles', 'family'])

with open(fname_executives, 'r', encoding='utf-8') as f:
    executives_df = pd.json_normalize(yaml.safe_load(f))
assert all(executives_df.columns == ['terms', 'id.bioguide', 'id.govtrack', 'id.icpsr_prez', 'name.first', 'name.last', 'bio.birthday', 'bio.gender', 'id.icpsr', 'name.suffix', 'name.middle', 'id.thomas', 'name.nickname', 'id.lis', 'id.opensecrets', 'id.votesmart', 'id.fec', 'id.cspan', 'id.wikipedia', 'id.wikidata', 'id.google_entity_id', 'id.ballotpedia', 'id.house_history', 'id.maplight', 'name.official_full'])

conn1 = sqlite3.connect(fname1)
cursor_1 = conn1.cursor()
cursor_1.execute('PRAGMA foreign_keys = ON')
conn2 = sqlite3.connect(fname2)
cursor_2 = conn2.cursor()
cursor_2.execute('PRAGMA foreign_keys = ON')
cursors = [cursor_1, cursor_2]
conns = [conn1, conn2]

state_abbrev = dict(Alabama='AL', Alaska='AK', Arizona='AZ', Arkansas='AR', California='CA', Colorado='CO',
                    Connecticut='CT', Delaware='DE', Florida='FL', Georgia='GA', Hawaii='HI', Idaho='ID',
                    Illinois='IL', Indiana='IN', Iowa='IA', Kansas='KS', Kentucky='KY', Louisiana='LA',
                    Maine='ME', Maryland='MD', Massachusetts='MA', Michigan='MI', Minnesota='MN',
                    Mississippi='MS', Missouri='MO', Montana='MT', Nebraska='NE', Nevada='NV',
                    New_Hampshire='NH', New_Jersey='NJ', New_Mexico='NM', New_York='NY', North_Carolina='NC',
                    North_Dakota='ND', Ohio='OH', Oklahoma='OK', Oregon='OR', Pennsylvania='PA',
                    Rhode_Island='RI', South_Carolina='SC', South_Dakota='SD', Tennessee='TN',
                    Texas='TX', Utah='UT', Vermont='VT', Virginia='VA', Washington='WA',
                    West_Virginia='WV', Wisconsin='WI', Wyoming='WY', District_of_Columbia='DC')
state_abbrev_backward = {v:k for k,v in state_abbrev.items()}
for cursor in cursors:
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS States
          (sid INTEGER PRIMARY KEY AUTOINCREMENT,
           state_name TEXT,
           state_abbreviation CHAR(2),
           state_capital TEXT,
           capital_latitude FLOAT,
           capital_longitude FLOAT,
           state_population INTEGER)''')
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS Politicians
          (pid INTEGER PRIMARY KEY AUTOINCREMENT,
           first_name CHAR(20),
           last_name CHAR(20),
           full_name TEXT,
           birthday DATE,
           gender CHAR(1)) ''')
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS Terms
          (tid INTEGER PRIMARY KEY AUTOINCREMENT,
           term_type TEXT,
           start_date DATE,
           end_date DATE,
           party CHAR(20),
           how_in_office CHAR(20),
           pid INTEGER,
           district INTEGER,
           sid INTEGER,
           FOREIGN KEY(sid) REFERENCES States(sid),
           FOREIGN KEY(pid) REFERENCES Politicians(pid))''')
    cursor.connection.commit()

def insert_legislator(cursor, term, state_abbrev_backward): # pylint: disable=redefined-outer-name
    '''Given a term and the state abbreviation, add a legislator'''
    try:
        term_state_name = state_abbrev_backward[term['state']].replace('_', ' ')
        sid = int(states_df.query(f'state_name == "{term_state_name}"')['sid'].iloc[0])
    except:  # pylint: disable=bare-except
        sid = None   # Eleanor Holms Norton from DC, which is not a state

    cursor.execute('''INSERT INTO Terms ( term_type,  start_date,  end_date,
                                          party,  how_in_office, district,
                                          pid,  sid)
                                 VALUES (:term_type, :start_date, :end_date,
                                         :party, :how_in_office, :district,
                                         :pid, :sid)''',
                   dict(term_type=term_type_dict[term['type']], start_date=term['start'],
                        end_date=term['end'], party=term.get('party', 'no party'),
                        how_in_office=term.get('how', 'election'),
                        pid=pid,
                        sid=sid, district=term.get('district', None)))

for cursor in cursors:
    for index, row in states_df.iterrows():
        cursor.execute('''INSERT INTO States ( state_name,  state_capital,
                                               state_population, state_abbreviation,
                                               capital_latitude,  capital_longitude)
                                      VALUES(:state_name, :state_capital,
                                             :state_population, :state_abbrev,
                                             :capital_latitude, :capital_longitude)''',
                       dict(state_name=row['state_name'], state_capital=row['state_capital'],
                            state_population=row['state_population'],
                            state_abbrev=state_abbrev[row['state_name'].replace(' ', '_')],
                            capital_latitude=row['capital_latitude'], capital_longitude=row['capital_longitude']))
        states_df.loc[index, 'sid'] = int(cursor.lastrowid)
    # states_df.to_sql('States', conn, if_exists='replace', index=False)
    cursor.connection.commit()

for cursor in cursors:
    for index, row in executives_df.iterrows():
        if 'name.middle' in row and isinstance(row['name.middle'], str) and row['name.middle'] != 'nan':
            full_name = f"{row['name.first']} {row['name.middle']} {row['name.last']}"
        else:
            full_name = f"{row['name.first']} {row['name.last']}"
        cursor.execute('''INSERT INTO Politicians ( first_name,  last_name, full_name,
                                                    birthday,  gender )
                                           VALUES (:first_name, :last_name, :full_name,
                                                   :birthday, :gender)''',
                       dict(first_name=row['name.first'], last_name=row['name.last'],
                            full_name=full_name,
                            birthday=row['bio.birthday'], gender=row['bio.gender']))
        pid = cursor.lastrowid
        executives_df[index, 'pid'] = pid

        # Insert the politician's terms from the executive branch or the historical legislator branch
        bool_array = (legislators_historical_df['id.bioguide'] == row['id.bioguide']) | \
                     (legislators_historical_df['id.govtrack'] == row['id.govtrack'])
        if any(bool_array):
            for term in legislators_historical_df[bool_array]['terms'].iloc[0]:
                if term['type'] != 'prez' and term['type'] != 'viceprez':
                    insert_legislator(cursor, term, state_abbrev_backward)
        for term in row['terms']:
            cursor.execute('''INSERT INTO Terms ( term_type,  start_date,  end_date,
                                                  party,  how_in_office, district,
                                                  pid,  sid)
                                         VALUES (:term_type, :start_date, :end_date,
                                                 :party, :how_in_office, :district,
                                                 :pid, :sid)''',
                           dict(term_type=term_type_dict[term['type']], start_date=term['start'],
                                end_date=term['end'], party=term.get('party', 'no party'),
                                how_in_office=term.get('how', 'election'),
                                pid=pid,
                                sid=None, district=None # executives not from state/district
                                ))
    cursor.connection.commit()

for cursor in cursors:
    for index, row in legislators_current_df.iterrows():
        if 'name.middle' in row and isinstance(row['name.middle'], str) and row['name.middle'] != 'nan':
            full_name = f"{row['name.first']} {row['name.middle']} {row['name.last']}"
        else:
            full_name = f"{row['name.first']} {row['name.last']}"
        cursor.execute('''INSERT INTO Politicians ( first_name,  last_name,  full_name,
                                                    birthday,  gender )
                                           VALUES (:first_name, :last_name, :full_name,
                                                   :birthday, :gender)''',
                       dict(first_name=row['name.first'], last_name=row['name.last'],
                            full_name=full_name,
                            birthday=row['bio.birthday'], gender=row['bio.gender']))
        pid = cursor.lastrowid
        legislators_current_df[index, 'pid'] = pid
        for term in row['terms']:
            insert_legislator(cursor, term, state_abbrev_backward)
    cursor.connection.commit()

# Elect Alfred E. Newman President
cursor = cursors[1]
cursor.execute('''INSERT INTO Politicians ( first_name,  last_name,  full_name,
                                            birthday,  gender )
                                   VALUES ('Alfred', 'Neuman', 'Alfred E. Neuman',
                                           '1925-10-24', 'T')''')
pid = cursor.lastrowid
cursor.execute('''INSERT INTO Terms ( term_type,  start_date,  end_date,
                                      party,  how_in_office, district,
                                      pid,  sid)
                             VALUES ('President', '2025-01-20', '2029-01-20',
                                     'Mad Magazine', 'write-in', :district, :pid, :sid)''',
               dict(pid=pid, district=None, sid=None))
cursor.connection.commit()

# Swap state abbreviations
cursor.execute('''UPDATE States SET state_abbreviation='AK' WHERE state_name='Alabama' ''')
cursor.execute('''UPDATE States SET state_abbreviation='AL' WHERE state_name='Alaska' ''')
cursor.execute('''UPDATE States SET state_abbreviation='TX' WHERE state_name='Tennessee' ''')
cursor.execute('''UPDATE States SET state_abbreviation='TN' WHERE state_name='Texas' ''')
cursor.connection.commit()


# Two states with the same population
cursor.execute('''UPDATE States SET state_population=(SELECT state_population FROM States WHERE state_name='California') WHERE state_name='Texas'  ''')
cursor.execute('''UPDATE States SET state_population=(SELECT state_population FROM States WHERE state_name='Wyoming') WHERE state_name='Vermont'  ''')
cursor.connection.commit()

cursor.execute('''SELECT sql
                    FROM sqlite_schema
                   WHERE type='table' ''')
schema = re.sub("\n  *",
                "\n     ",
                "\n".join([x[0] for x in cursor.fetchall()]))
schema = re.sub(r'CREATE TABLE sqlite_sequence\(name,seq\)\n', '', schema)
with open(fname1.replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
    json.dump(schema, fid)
