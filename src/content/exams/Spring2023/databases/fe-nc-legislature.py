#!/usr/bin/env python
""" Create Legislature """

# pylint: disable=line-too-long, invalid-name, consider-using-with

from contextlib import closing
from collections import namedtuple
import json
import os
import zipfile
import base64
import io
import re
import sqlite3
import pdb

# from legcop import LegiScan

# LegiScan User manual https://legiscan.com/gaits/documentation/legiscan
# https://github.com/poliquin/pylegiscan
# pip install legcop
# API https://legiscan.com/legiscan
# https://pypi.org/project/legcop/
# LEGISCAN_KEY = "4d1fe890aad94c11701136d1a3b2d853"
# LEGISCAN_KEY = "ea2baffb44425505638b99afdbba0914"
STATE = 'NC'
YEAR_START = 2021
YEAR_END = 2022
# getDatasetList	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getDatasetList&state=NC
# getDataset	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getDataset&access_key=3w01wOXGmwqiG1MS0UYJPV&id=2032
# getSessionList	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getSessionList&state=NC
# getSessionPeople	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getSessionPeople&id=2032
# getMonitorListRaw	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getMonitorListRaw&record=current
# getMonitorList	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getMonitorList&record=all
# getMasterListRaw	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getMasterListRaw&id=2032
# getMasterList	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getMasterList&id=2032
# getBill	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getBill&id=1721698
# getBillText	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getBillText&id=2719614
# getAmendment	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getAmendment&id=150034
# getSupplement	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getSupplement&id=312384
# getRollCall	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getRollCall&id=1259288
# getPerson	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getPerson&id=24890
# getSearch	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getSearch&state=NC&query=tax
# getSearchRaw	https://api.legiscan.com/?key=4d1fe890aad94c11701136d1a3b2d853&op=getSearchRaw&state=NC&query=tax

# pylint: disable=line-too-long, invalid-name, forgotten-debug-statement, too-many-lines, redefined-outer-name, bare-except, too-many-branches

# Get the LegiScan object
# legis = LegiScan(LEGISCAN_KEY)


DATABASES = ['fe-nc-legislature-1.sqlite', 'fe-nc-legislature-2.sqlite']

# Get the session list
# nc_sessions = legis.get_session_list(state='NC')
# this_session = None
# for session in nc_sessions:
#     if session['year_start'] == YEAR_START and session['year_end'] == YEAR_END:
#         this_session = session
#         break
# else:
#     assert False, f'The start/end year of {YEAR_START}/{YEAR_END} is not in {[(x["year_start"]/x["year_end"]) for x in nc_sessions]}'

# Get the data set list
# datasetlist = legis.get_dataset_list(state='NC', year =YEAR_START)
# access_key = datasetlist[0]['access_key']
# session_id = datasetlist[0]['session_id']

# Get the dataset
# dataset = legis.get_dataset(session_id=session_id, access_key=access_key)
# assert dataset['status'] == 'OK'
# readable_dataset = legis.recode_zipfile(dataset)
with open('NCLegislature.dataset.json', encoding='UTF-8') as fid:
    dataset = json.load(fid)
zipped_data = dataset['dataset']['zip']
base64_bytes = zipped_data.encode('ascii')
message_bytes = base64.b64decode(base64_bytes)
readable_dataset = zipfile.ZipFile(io.BytesIO(message_bytes))

# legislators = legis.get_session_people(session_id)
with open('NCLegislature.people.json', encoding='UTF-8') as fid:
    legislators_request = json.load(fid)
legislators = legislators_request['sessionpeople']['people']

# Remove old databases
conns = []
for db in DATABASES:
    if os.path.exists(db):
        os.remove(db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.cursor().execute('PRAGMA foreign_keys = ON')
    conns.append(conn)


POLITICAL_PARTY_DICT = {'1': 'Democratic',
                          '2': 'Republican',
                          '3': 'Independent',
                          '4': 'Green',
                          '5': 'Libertarian',
                          '6': 'Nonpartisan'}
BILL_STATUS_MAP = { 1: 'Introduced',
                   4: 'Passes',
                   5: 'Vetoed'}
VOTE_MAP = {1: 'Yea',
            2: 'Nay',
            3: 'Abstain',
            4: 'Absent'}

def standardize_legislator(legislator):
    ''' Do all standardizations for legislators; Don't use if False returned '''
    if legislator['committee_id'] > 0:
        return False

    #  Given a legislator, set the database value of role
    if legislator['role'] not in ['Representative', 'Senator']:
        # The values have not been previously updated
        if legislator['role'] == 'Rep':
            legislator['role'] = 'Representative'
        elif legislator['role'] == 'Sen':
            legislator['role'] = 'Senator'
        else:
            assert False, f'Legislator role "{legislator["role"]}"'

    # Given a legislator, set the database value of party
    # From https://legiscan.com/misc/LegiScan_API_User_Manual.pdf pge 41
    assert '1' <= legislator['party_id'] <= '6', legislator
    legislator['party'] = POLITICAL_PARTY_DICT[legislator['party_id']]
    legislator['legislator_id'] = legislator['people_id']
    return True

for index, conn in enumerate(conns):
    with closing(conn.cursor()) as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f'''
           CREATE TABLE Legislators
               (legislator_id INTEGER PRIMARY KEY,
                party TEXT CHECK(party IN {tuple(POLITICAL_PARTY_DICT.values())}),
                role text CHECK(role IN ('Senator', 'Representative')),
                name text,
                first_name text,
                middle_name text,
                last_name text,
                district text CHECK(SUBSTR(district, 1,3) IN ('HD-', 'SD-')) -- Start with HD for House and SD for Senate
                )''')

        for legislator in legislators:
            if not standardize_legislator(legislator):
                continue
            cursor.execute('''INSERT INTO Legislators (party, role, name, first_name,
                                                          legislator_id,
                                                          middle_name, last_name, district)
                                               VALUES (:party, :role, :name, :first_name,
                                                       :legislator_id,
                                                       :middle_name, :last_name, :district)''',
                       dict(legislator))
        conn.commit()

def standardize_bill(bill):
    ''' Do all standardizations for bills; Don't use if False returned '''
    if 'bill' not in bill:
        return False
    if bill['bill']['bill_type_id'] != '1':
        if bill['bill']['bill_type_id'] not in ['R']:
            # Ignore resolutions
            return False
        print(bill['bill'])
        pdb.set_trace()
        return False

    # Status values p 42 https://legiscan.com/misc/LegiScan_API_User_Manual.pdf
    if bill['bill']['status'] not in BILL_STATUS_MAP.keys() and \
       bill['bill']['status'] not in BILL_STATUS_MAP.values():  # pylint: disable=consider-iterating-dictionary
        return False
    if bill['bill']['status'] not in BILL_STATUS_MAP.values():  # pylint: disable=consider-iterating-dictionary
        bill['bill']['status' ] = BILL_STATUS_MAP[bill['bill']['status']]

    # Use the NC Legislator website URL
    bill['bill']['url'] = bill['bill']['state_link']
    return True

def standardize_roll_call(cursor, roll_call):
    ''' Do all standardizations for roll_call; Don't use if False returned '''
    if 'roll_call' not in roll_call:
        if 'bill' not in roll_call:
            if 'person' not in roll_call:
                pdb.set_trace()
                print(roll_call.keys())
        return False
    if roll_call['roll_call']['chamber'] == 'H':
        roll_call['roll_call']['chamber'] = 'House'
    elif roll_call['roll_call']['chamber'] == 'S':
        roll_call['roll_call']['chamber'] = 'Senate'
    roll_call['roll_call']['not_voting'] = roll_call['roll_call']['nv']
    roll_call['roll_call']['description'] = roll_call['roll_call']['desc']
    roll_call['roll_call']['status_date'] = roll_call['roll_call']['date']
    cursor.execute('''SELECT bill_id FROM Bills where bill_id=:bill_id''',
                   roll_call['roll_call'])
    bill_id = cursor.fetchone()
    if not bill_id or not bill_id['bill_id']:
        # print(f"Roll call {roll_call['roll_call']['roll_call_id']} references",
        #       f"bill {roll_call['roll_call']['bill_id']}, but it doesn't exist.")
        return False
    return True

for index, conn in enumerate(conns):
    with closing(conn.cursor()) as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute(f'''
           CREATE TABLE Bills
               (bill_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT CHECK(status IN {tuple(BILL_STATUS_MAP.values())}),
                status_date TEXT, -- YYYY-MM-DD
                url TEXT) -- URL to NC Legislator website on bill
                ''')
        cursor.execute('''
           CREATE TABLE Roll_calls
               (roll_call_id INTEGER PRIMARY KEY,
                bill_id INTEGER REFERENCES Bills(bill_id) NOT NULL,
                description TEXT,
                date TEXT, -- YYYY-MM-DD if available
                yea INTEGER UNSIGNED, -- Count of Yeas
                nay INTEGER UNSIGNED, -- Count of Nays
                not_voting INTEGER UNSIGNED, -- Count of not voting
                absent INTEGER UNSIGNED, -- Count of absent
                passed INTEGER CHECK(passed IN (0, 1)),
                status_date TEXT, -- YYYY-MM-DD
                chamber TEXT CHECK(chamber IN ('House', 'Senate')))''')
        cursor.execute(f'''
           CREATE TABLE Votes
               (roll_call_id INTEGER REFERENCES Roll_calls(Roll_call_id),
                legislator_id INTEGER REFERENCES Legislators(legislator_id) NOT NULL,
                vote_text TEXT CHECK(vote_text IN {tuple(VOTE_MAP.values())}),
                UNIQUE(roll_call_id, legislator_id))
                ''')
        cursor.execute('''
           CREATE TABLE Sponsors
               (bill_id INTEGER REFERENCES Bills(bill_id),
                legislator_id INTEGER REFERENCES Legislators(legislator_id) NOT NULL,
                UNIQUE(bill_id, legislator_id))
                ''')
        cursor.execute('''
           CREATE TABLE Subject_names
               (subject_id INTEGER PRIMARY KEY,
                subject_name TEXT,
                UNIQUE(subject_name))
                ''')
        cursor.execute('''
           CREATE TABLE Bill_subjects
               (subject_id INTEGER REFERENCES Subject_names(subject_id) NOT NULL,
                bill_id INTEGER REFERENCES Bills(bill_id) NOT NULL,
                UNIQUE(subject_id, bill_id))
                ''')

        legislation_data = []
        for name in readable_dataset.namelist():
            if name in ['NC/2021-2022_Regular_Session/LICENSE', \
                        'NC/2021-2022_Regular_Session/hash.md5', \
                        'NC/2021-2022_Regular_Session/README.md']:
                continue
            data = readable_dataset.read(name).decode('UTF-8')
            try:
                legislation_data.append(json.loads(data))
            except:
                pdb.set_trace()
                print(data)

        for index, legislation in enumerate(legislation_data):
            if not standardize_bill(legislation):
                # Print out resolutions
                # if 'bill' in legislation:
                #     print(legislation['bill']['title'])
                continue
            cursor.execute(''' INSERT INTO Bills (bill_id, title, status, status_date, url)
                                           VALUES(:bill_id, :title, :status, :status_date, :url)''',
                           legislation['bill'])

        # Once all bills are taken care of, can insert data that references bills
        for legislation in legislation_data:
            if not standardize_roll_call(cursor, legislation):
                continue
            cursor.execute(''' INSERT INTO Roll_calls (roll_call_id, bill_id, date, yea, nay,
                                                       not_voting, passed, absent, description,
                                                       chamber, status_date)
                                           VALUES(:roll_call_id, :bill_id, :date, :yea, :nay,
                                                  :not_voting, :passed, :absent, :description,
                                                  :chamber, :status_date)''',
                           legislation['roll_call'])
            for vote in legislation['roll_call']['votes']:
                cursor.execute('''INSERT INTO Votes (roll_call_id, legislator_id, vote_text)
                                              VALUES(:roll_call_id, :legislator_id, :vote_text)''',
                               dict(roll_call_id=legislation['roll_call']['roll_call_id'],
                                    legislator_id=vote['people_id'],
                                    vote_text=VOTE_MAP[vote['vote_id']]))

        # Once all bills and people are in, add sponsors, subjects
        for index, legislation in enumerate(legislation_data):
            if not standardize_bill(legislation):
                continue

            if 'sponsors' in legislation['bill']:
                for sponsor in legislation['bill']['sponsors']:
                    if not standardize_legislator(sponsor):
                        continue
                    cursor.execute(''' INSERT INTO Sponsors (bill_id, legislator_id)
                                           VALUES(:bill_id, :sponsor_id) ''',
                                   dict(bill_id=legislation['bill']['bill_id'],
                                        sponsor_id=sponsor['people_id']))
            if 'subjects' in legislation['bill']:
                for subject in legislation['bill']['subjects']:
                    cursor.execute('''INSERT INTO Subject_names (subject_id, subject_name)
                                                    SELECT :subject_id, :subject_name
                                                     WHERE NOT EXISTS (SELECT *
                                                                         FROM Subject_names
                                                                       WHERE subject_id=:subject_id)''',
                                   subject)
                    cursor.execute('''INSERT INTO Bill_subjects (subject_id, bill_id)
                                                         VALUES (:subject_id, :bill_id)''',
                                   dict(subject_id=subject['subject_id'],
                                        bill_id=legislation['bill']['bill_id']))
            # What to do with amendments, committees

        conn.commit()

# Update second database for Partisans
BOGUS = namedtuple('BOGUS', 'party role legislator_id name first_name middle_name last_name district')
bogus_politician = dict(
    Representative=dict(Democratic=BOGUS(party='Democratic', role='Representative',
                                         legislator_id=1111, name='Samuel James Ervin, Jr',
                                         first_name='Sam', middle_name='James', last_name='Ervin',
                                         district='HD-86'),
                        Republican=BOGUS(party='Republican', role='Representative',
                                         legislator_id=2222, name='Ada Fisher',
                                         first_name='Ada', middle_name='A.', last_name='Fisher',
                                         district='HD-4')),
    Senator=dict(Democratic=BOGUS(party='Democratic', role='Senator',
                                legislator_id=3333, name='James K. Polk',
                                first_name='James', middle_name='K.', last_name='Polk',
                                district='SD-50'),
                 Republican=BOGUS(party='Republican', role='Senator',
                                  legislator_id=4444, name='Jesse Helms, Jr',
                                  first_name='Jesse', middle_name='Alexander', last_name='Helms',
                                  district='SD-35')))
with closing(conns[1].cursor()) as cursor:
    # Add famous NC democrats and republicans
    for party in ['Democratic', 'Republican']:
        for role in ['Representative', 'Senator']:
            this_bogus = bogus_politician[role][party]
            cursor.execute('''INSERT INTO Legislators (party, role, name, first_name,
                                                       legislator_id,
                                                       middle_name, last_name, district)
                                               VALUES (:party, :role, :name, :first_name,
                                                       :legislator_id,
                                                       :middle_name, :last_name, :district)''',
                           dict(party=this_bogus.party, role=this_bogus.role,
                                name=this_bogus.name, first_name=this_bogus.first_name,
                                middle_name=this_bogus.middle_name, last_name=this_bogus.last_name,
                                legislator_id=this_bogus.legislator_id,
                                district=this_bogus.district))
    conn.commit()

# Update second database for Bill.Most.Sponsors
with closing(conns[1].cursor()) as cursor:
    # Add more sponsors to the second most sponsored bill
    for chamber in ['Senate', 'House']:
        cursor.execute('''
          WITH Roll_Call_Counts AS (SELECT COUNT(*) as bill_count, bill_id
                                      FROM Roll_calls R
                                     WHERE chamber = :chamber 
                                     GROUP BY R.bill_id),
               Most_roll_calls AS (SELECT bill_id, bill_count
                                     FROM Roll_Call_Counts
                                    WHERE bill_count = (SELECT MAX(bill_count)
                                                          FROM Roll_Call_Counts)),
               Other_than_most AS (SELECT bill_count, bill_id
                                     FROM Roll_Call_Counts
                                    WHERE bill_id not in (SELECT bill_id
                                                          FROM Most_roll_Calls))
               SELECT COUNT(*) as bill_count, bill_id
                 FROM Roll_calls R
                WHERE chamber = :chamber 
                GROUP BY bill_id
               HAVING count(*) = (SELECT MAX(bill_count)
                                    FROM Other_than_most)
                    UNION
               SELECT bill_count, bill_id
                 FROM Most_roll_calls
                      ''',
                       dict(chamber=chamber))
        rows = cursor.fetchall()
        penultimate_info = rows[0]
        max_info = rows[-1]
        num_to_add = max_info['bill_count'] - penultimate_info['bill_count']
        for index in range(num_to_add):
            # Add the bogus_politician
            cursor.execute('''
              INSERT INTO Roll_Calls (description, bill_id, chamber, date, Yea, Nay, not_voting, absent, passed, status_date, chamber)
                            VALUES(:description, :bill_id, :chamber, :date, :yea, :nay, :not_voting, :absent, :passed, :status_date, :chamber)''',
                           dict(description=f'John\'s vote {index+1}',
                                bill_id=penultimate_info['bill_id'],
                                date='2023-05-09', yea=0, nay=0, not_voting=0, absent=0,
                                passed=0, status_date='2022-05-09', chamber=chamber))
        if chamber == 'Senate':
            cursor.execute('''INSERT INTO Sponsors (bill_id, legislator_id)
                                            VALUES (:bill_id, :legislator_id)''',
                           dict(bill_id=penultimate_info['bill_id'],
                                legislator_id=bogus_politician['Senator']['Democratic'].legislator_id))
            cursor.execute('''INSERT INTO Sponsors (bill_id, legislator_id)
                                            VALUES (:bill_id, :legislator_id)''',
                           dict(bill_id=penultimate_info['bill_id'],
                                legislator_id=bogus_politician['Senator']['Republican'].legislator_id))
        else:
            cursor.execute('''INSERT INTO Sponsors (bill_id, legislator_id)
                                            VALUES (:bill_id, :legislator_id)''',
                           dict(bill_id=penultimate_info['bill_id'],
                                legislator_id=bogus_politician['Representative']['Democratic'].legislator_id))
            cursor.execute('''INSERT INTO Sponsors (bill_id, legislator_id)
                                            VALUES (:bill_id, :legislator_id)''',
                           dict(bill_id=penultimate_info['bill_id'],
                                legislator_id=bogus_politician['Representative']['Republican'].legislator_id))
    conn.commit()

# Update second database Subjects by party
with closing(conns[1].cursor()) as cursor:
    # Add more sponsors to the second most sponsored bill
    cursor.execute('SELECT max(subject_id) as subject_id from Subject_names')
    max_subject_id = int(cursor.fetchone()['subject_id'])
    cursor.execute('SELECT max(bill_id) as bill_id FROM Bills')
    max_bill_id = int(cursor.fetchone()['bill_id'])
    for party in ['Democratic', 'Republican']:
        for role in ['Representative', 'Senator']:
            max_subject_id += 1
            cursor.execute(f'''
               INSERT INTO Subject_names (subject_id, subject_name)
                                  VALUES ({max_subject_id}, 'Bogus {party} {"House" if role=="Representative" else "Senate"} Subject')''')
            cursor.execute(f'''
               INSERT INTO Sponsors (bill_id, legislator_id)
                             VALUES ({max_bill_id}, {bogus_politician[role][party].legislator_id})''')
            cursor.execute(f'''
               INSERT INTO Bill_subjects (bill_id, subject_id)
                             VALUES ({max_bill_id}, {max_subject_id})''')
    conn.commit()


# Get the schema
with closing(conns[0].cursor()) as cursor:
    cursor.execute('''SELECT sql
                        FROM sqlite_schema
                       WHERE type='table'  ''')
    schema = re.sub("\n  *",
                   "\n     ",
                   "\n".join([x[0] for x in cursor.fetchall()]))
    schema = re.sub(r'CREATE TABLE sqlite_sequence\(name,seq\)\n', '', schema)
    with open(DATABASES[0].replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
        json.dump(schema, fid)
