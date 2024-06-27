#!/usr/bin/env python3
"""A script to create a sql nuclear meltdown escape room """

# pylint: disable=invalid-name, too-many-locals, too-many-branches, too-many-function-args
import json
import os
import random
import re
import sqlite3
from contextlib import closing
from collections import namedtuple
from datetime import datetime, timedelta, date

from faker import Faker
from faker_vehicle import VehicleProvider  # pip install faker_vehicle

# Since long text entered, ignore line-too-long pylint warnings along with cursor names
# pylint: disable=line-too-long, redefined-outer-name, invalid-name, too-many-arguments

NUM_TEAMS = 5
NUM_MEMBERS = 4
assert NUM_TEAMS < 10, f'NUM_TEAMS={NUM_TEAMS} but must be single digit for dictionary lookup'
assert NUM_MEMBERS < 10, f'NUM_MEMBERS={NUM_MEMBERS} but must be single digit for dictionary lookup'
NUM_DBS = NUM_TEAMS * NUM_MEMBERS + 1
NUM_EMPLOYEES = 25
MIN_ADDRESS = 10
MAX_ADDRESS = 1000
MIN_AGE = 16
MAX_AGE = 99
MIN_HEIGHT_MALE = 62
MAX_HEIGHT_MALE = 86
MIN_HEIGHT_FEMALE = 54
MAX_HEIGHT_FEMALE = 74
MEMBERSHIP_STATUSES = ['gold', 'silver', 'platinum']
EMPLOYEE_TYPES = ['contract-employee', 'permanent-employee', 'contractor', 'temporary', 'visitor']
HAIR_COLORS = ['black', 'brown', 'red', 'blond', 'white', 'blackish-red']
EYE_COLORS = ['brown', 'hazel', 'green', 'blue', 'grey']
THIS_YEAR = 2023

random.seed(0)
Faker.seed(0)
faker = Faker()
faker.add_provider(VehicleProvider)

# Create the faker items
male_first_names = [faker.first_name_male() for _ in range((NUM_DBS+1)//2)]
assert len(male_first_names) == (NUM_DBS+1) // 2
female_first_names = [faker.first_name_female() for _ in range((NUM_DBS+1)//2)]
assert len(female_first_names) == (NUM_DBS+1) // 2
last_names = [faker.last_name() for _ in range(NUM_DBS*2)]
assert len(last_names) == 2*NUM_DBS
phone_numbers = list({faker.phone_number().replace(' ', '-') for _ in range(3*NUM_DBS)})[:NUM_DBS]
assert len(set(phone_numbers)) == NUM_DBS
license_plates = [faker.license_plate().replace(' ', '-') for _ in range(NUM_DBS)]
assert len(set(license_plates)) == NUM_DBS
street_names = [faker.street_name() for _ in range(NUM_DBS+1)]
assert len(set(street_names)) == NUM_DBS+1
incident_dates = [datetime(THIS_YEAR, 1, 1) + timedelta(days=3*x) for x in range(NUM_DBS)]
assert len(set(incident_dates)) == NUM_DBS
company_names = list({faker.company() for _ in range(NUM_DBS)})
assert len(company_names) == NUM_DBS
POWER_COMPANY = dict(name='SQL City Nuclear Power Company',
                     address_number='123', address_street_name='Relational Blvd',
                     phone_number=faker.phone_number().replace(" ", "-"))
part_types = ['physical system', 'electrical', 'water', 'nuclear']
PART_NAME = namedtuple('PART_NAME', 'part_name part_type max_price min_price')
part_names = [PART_NAME(part_name='Control rods', part_type='nuclear', max_price=1000000, min_price=100000),
              PART_NAME(part_name='Fuel rods', part_type='nuclear', max_price=1000000, min_price=100000),
              PART_NAME(part_name='Reactor vessel', part_type='nuclear', max_price=10000000, min_price=1000000),
              PART_NAME(part_name='Water pump to reactor', part_type='water', max_price=70000, min_price=60000),
              PART_NAME(part_name='Water pump to steam generator', part_type='water', max_price=80000, min_price=70000),
              PART_NAME(part_name='Water pump to cooling towers', part_type='water', max_price=80000, min_price=70000),
              PART_NAME(part_name='Condenser', part_type='water', max_price=90000, min_price=70000),
              PART_NAME(part_name='Turbine bearings', part_type='physical system', max_price=20000, min_price=10000),
              PART_NAME(part_name='Turbine blades', part_type='physical system', max_price=30000, min_price=20000),
              PART_NAME(part_name='Steam generator', part_type='physical system', max_price=100000, min_price=90000),
              PART_NAME(part_name='Electric generator', part_type='electrical', max_price=200000, min_price=190000)]
assert all(x.part_type in part_types for x in part_names)
assert all(x.max_price>x.min_price for x in part_names)
IMPORTANT_ROOM_NAMES = ['Containment room', 'Auxiliary room', 'Control Room',
                        'Turbine room', 'Transformer room', 'Diesel generator I',
                        'Diesel generator II', 'Transformer room']
UNIMPORTANT_ROOM_NAMES = ['Vestibule', 'Machine shop']
ROOM_NAMES = UNIMPORTANT_ROOM_NAMES + IMPORTANT_ROOM_NAMES
START_DATE = date(2021, 1,1)

def json_serial(obj):
    '''JSON serializer for objects not serializable by default json code'''
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializeable")

def sqlite_date_time(this_date):
    ''' Return the date object in string YYYY-MM-DD HH:MM:SS format'''
    return this_date.strftime('%Y-%m-%d %H:%M%S')

def sqlite_date(this_date):
    ''' Return the date object in string YYYY-MM-DD format'''
    return this_date.strftime('%Y-%m-%d')

def create_tables(conn):
    '''Create The tables used for each database
       NOTE: This uses global variables, etc.  Bad.  But a hack to isolate all the noise data
    '''

    with closing(conn.cursor()) as cursor:
        cursor.execute('''CREATE TABLE Companies(
                                        id INTEGER PRIMARY KEY,
                                        name TEXT,
                                        address_number INTEGER,
                                        address_street_name TEXT,
                                        phone_number TEXT)''')

        cursor.execute(f'''CREATE TABLE Persons(
                                        id INTEGER PRIMARY KEY,
                                        name TEXT,
                                        address_number INTEGER,
                                        address_street_name TEXT,
                                        phone_number TEXT,
                                        employee_type TEXT,
                                        company_id INTEGER,
                                        CHECK (employee_type IN {tuple(EMPLOYEE_TYPES)}),
                                        FOREIGN KEY(company_id)
                                           REFERENCES Companies(id)
                                           ON DELETE CASCADE)''')

        cursor.execute('''CREATE TABLE Incident_Reports(
                                        id INTEGER PRIMARY KEY,
                                        incident_date TEXT,   -- 'YYYY-MM-DD'
                                        incident_type TEXT,
                                        description TEXT,
                                        persons_id INTEGER,
                                        FOREIGN KEY(persons_id)
                                           REFERENCES persons(id)
                                           ON DELETE CASCADE) ''')

        cursor.execute('''CREATE TABLE Drivers_License(
                                        id INTEGER PRIMARY KEY,
                                        persons_id INTEGER,
                                        expired BOOLEAN DEFAULT 0,
                                        age INTEGER,
                                        height_inches INTEGER,
                                        eye_color TEXT,
                                        hair_color TEXT,
                                        gender TEXT,
                                        plate_number TEXT,
                                        car_make TEXT,
                                        car_model TEXT,
                                        CHECK (expired IN (0, 1)),
                                        FOREIGN KEY(persons_id)
                                           REFERENCES Persons(id)
                                           ON DELETE CASCADE)''')

        cursor.execute('''CREATE TABLE Parts(
                                        id INTEGER PRIMARY KEY,
                                        company_id INTEGER,
                                        part_name TEXT,
                                        part_number TEXT,
                                        part_type TEXT,
                                        price REAL,
                                        installed BOOLEAN DEFAULT 0,
                                        CHECK (installed IN (0, 1)),
                                        FOREIGN KEY(company_id)
                                           REFERENCES Companies(id)
                                           ON DELETE CASCADE)''')

        cursor.execute('''CREATE TABLE Rooms(
                                        id INTEGER PRIMARY KEY,
                                        name TEXT,
                                        phone_number TEXT DEFAULT '') ''')

        cursor.execute('''CREATE TABLE Badge_Readers(
                                        id INTEGER PRIMARY KEY,
                                        from_room INTEGER,
                                        to_room INTEGER,
                                        FOREIGN KEY(from_room)
                                           REFERENCES Rooms(id)
                                           ON DELETE CASCADE,
                                        FOREIGN KEY(to_room)
                                           REFERENCES Rooms(id)
                                           ON DELETE CASCADE)''')

        cursor.execute('''CREATE TABLE Badges(
                                        id INTEGER PRIMARY KEY,
                                        persons_id INTEGER,
                                        rfid TEXT,
                                        expired BOOLEAN DEFAULT 0,
                                        CHECK (expired IN (0, 1)),
                                        FOREIGN KEY(persons_id)
                                           REFERENCES Persons(id)
                                           ON DELETE NO ACTION)''')

        cursor.execute('''CREATE TABLE Door_Opened(
                                        id INTEGER PRIMARY KEY,
                                        badge_id INTEGER,
                                        badge_reader_id INTEGER,
                                        open_time TIME, -- YYYY-MM-DD HH:MM:SS
                                        FOREIGN KEY(badge_reader_id)
                                           REFERENCES Badge_Readers(id)
                                           ON DELETE NO ACTION,
                                        FOREIGN KEY(badge_id)
                                           REFERENCES Badges(id)
                                           ON DELETE NO ACTION)''')

        cursor.connection.commit()

def write_schema(gd):
    ''' Create the schema and write it out '''
    conn = sqlite3.connect(gd['00']['database_fn'])
    with closing(conn.cursor()) as cursor:
        cursor.execute('''SELECT sql
                            FROM sqlite_schema
                           WHERE type='table'  ''')
        gd['schema'] = re.sub("\n  *",
                              "\n     ",
                              "\n".join([x[0] for x in cursor.fetchall()]))

    with open('game-nuclear.json', 'w', encoding='utf-8') as fid:
        json.dump(gd, fid, default=json_serial)

def insert_random_person(cursor, index, report_info, street_name=None, address_number=None,
                         eye_color=None, hair_color=None, gender=None,
                         car_make=None, car_model=None, plate_number=None,
                         employee_type=None, company_id=None,
                         phone_number=None, first_name=None, last_name=None):
    ''' Create random person info given an index '''
    if not address_number:
        address_number = random.randrange(MIN_ADDRESS, MAX_ADDRESS)
    if (index // 2 == 0 and gender is None) or gender == 'male':
        if not first_name:
            first_name = male_first_names[(index//2)%len(male_first_names)]
        gender = 'male'
        height = random.randrange(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
    else:
        if not first_name:
            first_name = female_first_names[(index//2)%len(female_first_names)]
        gender = 'female'
        height = random.randrange(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
    if not phone_number:
        phone_number = phone_numbers[(index*31) % len(phone_numbers)]
    if not last_name:
        last_name = last_names[(index*29)%len(last_names)]
    name = f'{first_name} {last_name}'
    age = random.randrange(MIN_AGE, MAX_AGE)
    vehicle = faker.vehicle_object()
    if not car_make:
        car_make = vehicle["Make"]
    if not car_model:
        car_model = vehicle["Model"]
    if not eye_color:
        eye_color = random.choice(EYE_COLORS)  # eye_colors[(index*17)%len(eye_colors)]
    if not hair_color:
        hair_color = random.choice(HAIR_COLORS)  # hair_colors[(index*13)%len(hair_colors)]
    if not street_name:
        street_name = street_names[(index*19)%len(street_names)]
    if not plate_number:
        plate_number = license_plates[(index*23)%len(license_plates)]
    if not employee_type:
        employee_type = random.choice(EMPLOYEE_TYPES)
    if company_id is None:  # company_id could be zero
        company_id = random.choice(POWER_COMPANY['all_ids'])

    cursor.execute(f'''DELETE FROM Persons  -- ensure unique name/phone_number
                             WHERE name='{name}' OR
                                   phone_number='{phone_number}' ''')
    cursor.execute(f'''INSERT INTO Persons (name, address_number, address_street_name, phone_number, employee_type, company_id)
                              VALUES ('{name}', {address_number}, '{street_name}', '{phone_number}', '{employee_type}', {company_id})  ''')
    persons_id = cursor.lastrowid

    # Add badges
    if index % 5 == 1:
        # Every five persons, add an expired drivers license
        cursor.execute(f'''INSERT INTO Badges(persons_id, expired, rfid)
                                  VALUES ({persons_id}, 1, '{faker.uuid4()}')''')
    cursor.execute(f'''INSERT INTO Badges(persons_id, expired, rfid)
                              VALUES ({persons_id}, 0, '{faker.uuid4()}')''')
    badge_id = cursor.lastrowid

    # Insert at least one door opening before the incident
    cursor.execute('SELECT id FROM Badge_Readers')
    badge_reader_ids = [x['id'] for x in cursor.fetchall()]
    cursor.execute(f'''INSERT INTO Door_Opened (badge_id, badge_reader_id, open_time)
                                   VALUES ({badge_id}, {random.choice(badge_reader_ids)},
                                           '{faker.date_time_between(START_DATE, report_info["incident_date"])}') ''')

    # Add driver's license
    if index % 10 == 0:
        # Every ten persons, add an expired drivers license
        cursor.execute(f'''INSERT INTO drivers_license(persons_id, age, height_inches, eye_color, hair_color,
                                                       gender, plate_number, car_make, car_model, expired)
                                  VALUES ({persons_id}, {age}, {height}, '{eye_color}', '{hair_color}',
                                          '{gender}', '{plate_number}', '{car_make}', '{car_model}', 1) ''')
    cursor.execute(f'''INSERT INTO drivers_license(persons_id, age, height_inches, eye_color, hair_color,
                                                   gender, plate_number, car_make, car_model)
                              VALUES ({persons_id}, {age}, {height}, '{eye_color}', '{hair_color}',
                                      '{gender}', '{plate_number}', '{car_make}', '{car_model}') ''')
    return persons_id


def create_contact(cursor, index, report_info):
    """ Create the outside contact """
    contact_info = {}
    if index % 2 == 0:
        contact_eye_color = random.choice(EYE_COLORS) # faker.color_name()
        wrong_eye_color = list(set(EYE_COLORS)-set(contact_eye_color))
        wrong_eye_color = wrong_eye_color[(index*19)%len(wrong_eye_color)]
        contact_hair_color = random.choice(HAIR_COLORS) # faker.color_name()
        wrong_hair_color = list(set(HAIR_COLORS)-set(contact_hair_color))
        wrong_hair_color = wrong_hair_color[(index*21)%len(wrong_hair_color)]
        contact_gender = ['male', 'female'][ (index // 2) % 2 ]
        wrong_gender = ['female', 'male'][ (index // 2) % 2 ]

        # Make sure there is only one with the contact's eye, hair, and gender
        cursor.execute(f'''DELETE FROM Drivers_License
                                WHERE eye_color='{contact_eye_color}' AND
                                      hair_color='{contact_hair_color}' AND
                                      gender='{contact_gender}' ''')
        persons_id = insert_random_person(cursor, index, report_info, eye_color=contact_eye_color,
                                          hair_color=contact_hair_color, gender=contact_gender)
        # Create 7 people with wrong eye, hair or gender or some combination
        for i in range(7):
            insert_random_person(cursor, index+i+1, report_info,
                                 eye_color=[wrong_eye_color, contact_eye_color][i%2],
                                 hair_color=[wrong_hair_color, contact_hair_color][(i//2)%2],
                                 gender=[wrong_gender, contact_gender][(i//4)%2])
        # Ensure uniqueness
        cursor.execute(f'''UPDATE Drivers_License SET expired=1
                                  WHERE eye_color='{contact_eye_color}' AND
                                        hair_color='{contact_hair_color}' AND
                                        gender='{contact_gender}' AND
                                        persons_id != {persons_id} AND
                                        expired=0''')
        contact_statement = f'''Watch the video, I'm the person who stopped the bad guys from coming in to kill you.
You can see me outside the control room fighting off the bad guys before you could lock the door.

Look at the video!  I'm a very distinctive {'man' if contact_gender=='male' else 'woman'} with my {contact_eye_color} colored eyes, and
{contact_hair_color} colored hair.

You need to trust me.'''
        contact_info['contact_type'] = 'color'
        contact_info['color'] = dict(eye_color=contact_eye_color,
                                     hair_color=contact_hair_color,
                                     contact_statement=contact_statement,
                                     gender=contact_gender)
    else:
        vehicle = faker.vehicle_object()  # Ensure different vehicle for unexpired license
        contact_car_make = vehicle["Make"]
        contact_car_model = vehicle["Model"]
        contact_plate_number = license_plates[ (index*13)%len(license_plates) ]
        wrong_vehicle = faker.vehicle_object()
        wrong_car_make = wrong_vehicle["Make"]
        wrong_car_model = wrong_vehicle["Model"]
        wrong_plate_number = list(set(license_plates)-set([contact_plate_number]))
        wrong_plate_number = wrong_plate_number[(index*23)%len(wrong_plate_number)]

        # Make sure there's only one with the contacts car make, model, and plate number
        cursor.execute(f'''DELETE FROM Drivers_License
                                WHERE car_make='{contact_car_make}' AND
                                      car_model='{contact_car_model}' AND
                                      plate_number='{contact_plate_number}'  ''')
        persons_id = insert_random_person(cursor, index, report_info,
                                          car_make=contact_car_make,
                                          car_model=contact_car_model,
                                          plate_number=contact_plate_number)

        # Create 7 people with wrong eye, hair or gender or some combination
        for i in range(7):
            insert_random_person(cursor, index+i+1, report_info,
                                 car_make=[wrong_car_make, contact_car_make][i%2],
                                 car_model=[wrong_car_model, contact_car_model][(i//2)%2],
                                 plate_number=[wrong_plate_number, contact_plate_number][(i//4)%2])

        cursor.execute(f'''UPDATE Drivers_License SET expired=1
                                  WHERE car_make='{contact_car_make}' AND
                                        car_model='{contact_car_model}' AND
                                        plate_number='{contact_plate_number}' AND
                                        persons_id != {persons_id} AND
                                        expired=0''')
        contact_statement = f'''Watch the video, I'm the person who stopped the bad guys from coming in to killyou.
You can see me drive up in my {contact_car_make} {contact_car_model} car
with licencse plate {contact_plate_number}.

Then you can see me lock the control room before the bad guys could get in to kill you.

You need to trust me.'''
        contact_info['contact_type'] = 'car'
        contact_info['car'] = dict(car_make=contact_car_make,
                                   contact_type='car',
                                   car_model=contact_car_model,
                                   contact_statement=contact_statement,
                                   plate_number=contact_plate_number)
    contact_info['persons_id'] = persons_id
    cursor.connection.row_factory = sqlite3.Row
    cursor.execute(f'''SELECT P.name, P.phone_number
                         FROM Persons AS P
                        WHERE id={persons_id}''')
    rows = cursor.fetchall()
    assert len(rows) == 1, f'''Don't know how, but there are {len(rows)} rows in Persons table with id={persons_id}'''
    contact_info['name'] = rows[0]['name']
    contact_info['phone_number'] = rows[0]['phone_number']

    # Ensure they have to put on the expired = 0
    # Create a driver's license with everything the same but the person_id
    cursor.execute(f'''INSERT INTO Drivers_License (persons_id,
                         expired, age, height_inches, eye_color, hair_color,
                         gender, plate_number, car_make, car_model)
                                   SELECT {int(contact_info['persons_id'])+1}, 1,
                                          age, height_inches, eye_color, hair_color,
                                          gender, plate_number, car_make, car_model
                                     FROM Drivers_License
                                    WHERE persons_id='{contact_info['persons_id']}' ''')
    return contact_info

def insert_random_report(cursor, index, incident_type=None, incident_date=None, incident_description=None, persons_id=None):
    ''' Create random incident report given an index '''
    descriptions = [faker.paragraph(nb_sentences=5, variable_nb_sentences=False) for _ in range(NUM_DBS)] + [
'''This job stinks.  I have been working security for years and no one reads these incident reports''',
'''Did you hear that Professor Majikes blather on and on and on?''']

    if not incident_type:
        incident_type = random.choice(['Serious', 'Alert', 'Code Red', 'Pants on fire', 'Note'])
    if not incident_date:
        incident_date =  datetime(THIS_YEAR, 1, 1) + [1,-1][index%2] * timedelta(days=4*index)
    if not incident_description:
        incident_description = random.choice(descriptions)
    if not persons_id:
        cursor.execute('''SELECT id FROM Persons''')
        persons_id = random.choice([x[0] for x in cursor.fetchall()])

    cursor.execute(f'''INSERT INTO Incident_Reports (incident_date, incident_type, description, persons_id)
                            VALUES ('{sqlite_date(incident_date)}',
                                    '{incident_type}', '{incident_description}', {persons_id}) ''')
    report_id = cursor.lastrowid
    return report_id


def create_reports(cursor, index, contact_info, report_info):
    ''' Create the initial incident report '''

    if contact_info['contact_type'] == 'color':
        incident_description = '''Tour of SQL Nuclear Power Plant by UNC software people.
They had to return to Chapel Hill, but left one really smart computer scientist.
I am going to leave the scientist in the control room as I go investigate some noise outside.'''
    else:
        incident_description = f'''I brought drove my {contact_info['car']['car_make']} {contact_info['car']['car_model']} to pick up a SQL expert from Chapel Hill.
After arriving, we had a tour of the control room.
I am going to leave the scientist in the control room as I go investigate some noise outside.'''

    # Insert random reports
    for _ in range(NUM_DBS):
        insert_random_report(cursor, index)

    # Make sure there are no other reports from the specified person on that day
    cursor.execute(f'''DELETE FROM Incident_Reports
                             WHERE incident_date='{report_info['incident_date_str']}' ''')
    insert_random_report(cursor, index, incident_date=report_info['incident_date'],
                         incident_description=incident_description, persons_id=contact_info['persons_id'])


def insert_companies(cursor, index):
    ''' Propogate the Companies table'''

    # Make sure SQL City Nuclear Power Company is in the companies list
    POWER_COMPANY['id'] = (index+1)*NUM_DBS
    cursor.execute(f'''INSERT INTO Companies
                                        (id, name, address_number,
                                         address_street_name, phone_number)
                                   VALUES({POWER_COMPANY['id']}, '{POWER_COMPANY["name"]}',
                                         '{POWER_COMPANY["address_number"]}',
                                         '{POWER_COMPANY["address_street_name"]}',
                                         '{POWER_COMPANY["phone_number"]}') ''')

    company_info = {}
    company_index = (index*13)%len(company_names)
    company_info['name'] = company_names[company_index]
    company_info['index'] = company_index
    p = part_names[(index*13)%len(part_names)]

    for company_index in range(NUM_DBS):
        address_number = random.randrange(MIN_ADDRESS, MAX_ADDRESS)
        street_name = street_names[(company_index*5)%len(street_names)]
        phone_number = faker.phone_number().replace(' ', '-')
        company_name = company_names[company_index%len(company_names)]

        cursor.execute(f'''INSERT INTO Companies
                                        (id, name, address_number,
                                         address_street_name, phone_number)
                                  VALUES({company_index}, '{company_name}', '{address_number}',
                                         '{street_name}', '{phone_number}') ''')
        for part_index, p in enumerate(part_names):
            if part_index == company_index % len(part_names) and company_name != company_info['name']:
                # Skip this part such that the company does not make all the parts
                continue
            cursor.execute(f'''INSERT INTO Parts (company_id, part_name, part_type,
                                                  part_number, price, installed)
                                           VALUES({company_index}, '{p.part_name}', '{p.part_type}',
                                                  '{faker.bothify(text="###-??-###")}', {random.randrange(p.min_price, p.max_price)},
                                                  {(part_index + index)%2})''')

    cursor.execute('SELECT id FROM Companies')
    POWER_COMPANY['all_ids'] = [x[0] for x in cursor.fetchall()]

    cursor.connection.commit()
    return company_info


def create_sabotaging_employees(cursor, report_info):
    ''' Create some random employees at the sabotaging company and two other companies '''
    temp = POWER_COMPANY['all_ids'].copy()
    temp.remove(company_info['index'])
    company_indexes = random.sample(temp, 2)
    company_indexes = [company_indexes[0], company_info['index'], company_indexes[1]]

    # Supply phone numbers and names because insert random person ensures unique by name/phone
    for i,c in enumerate(company_indexes):
        for j in range(NUM_EMPLOYEES//2+1):
            insert_random_person(cursor, NUM_DBS * (i + j + 1), report_info, company_id=c,
                                 phone_number=faker.phone_number().replace(' ', '-'),
                                 first_name=faker.first_name_male(), last_name=faker.last_name())
            insert_random_person(cursor, NUM_DBS * (i + j + 1), report_info, company_id=c,
                                 phone_number=faker.phone_number().replace(' ', '-'),
                                 first_name=faker.first_name_female(), last_name=faker.last_name())
            cursor.connection.commit()

def create_rooms(cursor):
    ''' Populate Rooms table, Badge_Readers table '''
    for i, room in enumerate(ROOM_NAMES):
        cursor.execute(f'''INSERT INTO Rooms (id, name, phone_number)
                                       VALUES({i}, '{room}', '{faker.phone_number().replace(' ', '-')}')  ''')

    # Ensure each room as an exit
    for to_room in range(len(ROOM_NAMES)):
        from_room = (to_room+1) % len(ROOM_NAMES)
        cursor.execute(f'''INSERT INTO Badge_Readers (from_room, to_room)
                                             VALUES({from_room}, {to_room}) ''')
        from_room = (to_room-1) % len(ROOM_NAMES)
        cursor.execute(f'''INSERT INTO Badge_Readers (from_room, to_room)
                                             VALUES({from_room}, {to_room}) ''')

    # Vestible to Auxilary, Machine shop to Vestibule
    cursor.execute(f'''INSERT INTO Badge_Readers (from_room, to_room)
                                         VALUES({ROOM_NAMES.index('Vestibule')}, {ROOM_NAMES.index('Auxiliary room')}) ''')
    cursor.execute(f'''INSERT INTO Badge_Readers (from_room, to_room)
                                         VALUES({ROOM_NAMES.index('Vestibule')}, {ROOM_NAMES.index('Machine shop')}) ''')
    cursor.connection.commit()

def create_saboteur_info(cursor, index, company_info, report_info):
    """ Create the information needed to identify the sabatour """
    unused = index  # pylint: disable=unused-variable
    company_name = company_info['name']
    saboteur_info = {}

    # Find the "middle person" in company who's not permanent as the sabatour
    cursor.connection.row_factory = sqlite3.Row
    cursor.execute(f'''SELECT P.id, P.name, P.employee_type, B.id as badge_id, DL.gender
                         FROM Persons AS P, Companies as C, Badges as B, Drivers_License as DL
                        WHERE C.name='{company_name}' AND
                              P.company_id=C.id AND
                              DL.id =B.persons_id AND
                              P.id=B.persons_id AND
                              P.employee_type != 'permanent-employee' ''')
    rows = cursor.fetchall()
    row = rows[ len(rows) // 2 ]
    saboteur_info['id'] = row['id']
    saboteur_info['name'] = row['name']
    saboteur_info['employee_type'] = row['employee_type']
    saboteur_info['badge_id'] = row['badge_id']
    saboteur_info['gender'] = row['gender']

    # Get all the important room id
    cursor.execute(f'''SELECT R.name, R.phone_number, R.id, BR.id as badge_reader_id
                         FROM Rooms as R, Badge_Readers as BR
                        WHERE R.name in {tuple(IMPORTANT_ROOM_NAMES)} AND
                              R.id = BR.to_room ''')
    ROOM_INFO = namedtuple('ROOM_INFO', 'id, phone_number badge_reader_id')
    rooms_info = {}
    for row in cursor.fetchall():
        if row['name'] not in rooms_info:
            rooms_info[row['name']] = ROOM_INFO(id=row['id'],
                                                badge_reader_id=row['badge_reader_id'],
                                                phone_number=row['phone_number'])


    # Insert at least one door opening before the incident
    for ri in rooms_info.values():
        for _ in range(10):
            cursor.execute(f'''INSERT INTO Door_Opened (badge_id, badge_reader_id, open_time)
                                   VALUES ({saboteur_info['badge_id']}, {ri.badge_reader_id},
                                           '{faker.date_time_between(START_DATE, report_info["incident_date"])}') ''')

    # Ensure there is one part installed with the saboteur's id
    cursor.execute(f'''UPDATE Parts
                          SET installed=true
                        WHERE id={saboteur_info['id']}''')

    return saboteur_info


index = 0
if __name__ == "__main__":
    # gameData will be the data shared with the worksheet in JSON format
    # databases will be indexed by f'{team}{member}'
    gameData = dict(NUM_TEAMS=NUM_TEAMS, NUM_MEMBERS=NUM_MEMBERS)


    for team in range(NUM_TEAMS+1):
        for member in range(NUM_MEMBERS):
            if team == NUM_TEAMS and member != 0:
                # game-nuclear-50 is the one we give out in the worksheet
                continue
            database_fn = f'game-nuclear{team}{member}.sqlite'
            if os.path.isfile(database_fn):
                os.remove(database_fn)
            conn = sqlite3.connect(database_fn)
            conn.row_factory = sqlite3.Row
            create_tables(conn)

            # When was the incident
            report_info = dict(incident_date=incident_dates[index],
                               incident_date_str=sqlite_date(incident_dates[index]))

            # Create rooms
            with closing(conn.cursor()) as cursor:
                create_rooms(cursor)

            # Insert companies
            with closing(conn.cursor()) as cursor:
                company_info = insert_companies(cursor, index)

            # Validate company info
            with closing(conn.cursor()) as cursor:
                cursor.execute('''  SELECT Z.name
                                      FROM Companies as Z
                                     WHERE NOT EXISTS (SELECT Y.part_name
                                                          FROM Parts as Y
                                                        EXCEPT
                                                        SELECT W.part_name
                                                          FROM Parts as W, Companies as X
                                                         WHERE X.name=Z.name AND
                                                               W.company_id = X.id)''')
                rows = cursor.fetchall()
                assert len(rows) == 1, f'For database {database_fn} the number of companies that make all parts is {len(rows)}'
                assert rows[0]['name'] == company_info['name'], f'For database {database_fn} the company who makes all parts is {rows[0]["name"]} but the company info is {company_info}'

            # create the random people
            with closing(conn.cursor()) as cursor:
                for j in range(NUM_DBS):
                    insert_random_person(cursor, j, report_info)
                cursor.connection.commit()

            with closing(conn.cursor()) as cursor:
                contact_info = create_contact(cursor, index, report_info)
                cursor.connection.commit()

            # create the random reports
            with closing(conn.cursor()) as cursor:
                for j in range(NUM_DBS):
                    insert_random_report(cursor, j)
                cursor.connection.commit()

            with closing(conn.cursor()) as cursor:
                create_reports(cursor, index, contact_info, report_info)
                cursor.connection.commit()

            # Validate report information
            with closing(conn.cursor()) as cursor:
                cursor.execute(f'''SELECT count(*)
                                     FROM incident_reports
                                    WHERE incident_date='{report_info['incident_date']}' ''')
                rows = cursor.fetchall()
                assert len(rows) ==1, f"Report info has {len(rows)} for: {database_fn} {report_info}"

            # Put in some random people at the sabotaging company (and two others)
            with closing(conn.cursor()) as cursor:
                create_sabotaging_employees(cursor, report_info)
                cursor.connection.commit()

            with closing(conn.cursor()) as cursor:
                saboteur_info = create_saboteur_info(cursor, index, company_info, report_info)
                cursor.connection.commit()

            # Validate contact information is unique if expired = 0
            with closing(conn.cursor()) as cursor:
                if contact_info['contact_type'] == 'color':
                    cursor.execute(f'''SELECT P.phone_number, I.incident_date
                                         FROM Drivers_License AS D, Persons AS P, Incident_Reports AS I
                                        WHERE P.id=D.persons_id AND
                                              P.id=I.persons_id AND
                                              I.incident_date='{report_info['incident_date_str']}' AND
                                              D.eye_color='{contact_info["color"]["eye_color"]}' AND
                                              D.hair_color='{contact_info["color"]["hair_color"]}' AND
                                              D.gender='{contact_info["color"]["gender"]}' AND
                                              D.expired=0''')
                else:
                    cursor.execute(f'''SELECT P.phone_number, I.incident_date
                                         FROM Drivers_License as D, Persons AS P, Incident_Reports AS I
                                        WHERE P.id=D.persons_id AND
                                              P.id=I.persons_id AND
                                              I.incident_date='{report_info['incident_date_str']}' AND
                                              D.car_model='{contact_info["car"]["car_model"]}' AND
                                              D.car_make='{contact_info["car"]["car_make"]}' AND
                                              D.plate_number='{contact_info["car"]["plate_number"]}' AND
                                              D.expired=0''')
                rows = cursor.fetchall()
                assert len(rows) == 1, f"Contact information has {len(rows)} for: {database_fn} {contact_info}"
                assert rows[0][0] == contact_info['phone_number'], f"Contact information has persons_id {rows[0][0]} for: {database_fn} {contact_info}"

            # Validate contact information is non-unique if expired = 1
            with closing(conn.cursor()) as cursor:
                if contact_info['contact_type'] == 'color':
                    cursor.execute(f'''SELECT DISTINCT P.phone_number
                                         FROM Drivers_License as D, Persons AS P
                                        WHERE D.eye_color='{contact_info["color"]["eye_color"]}' AND
                                              D.hair_color='{contact_info["color"]["hair_color"]}' AND
                                              D.persons_id=P.id AND
                                              D.gender='{contact_info["color"]["gender"]}' ''')
                else:
                    cursor.execute(f'''SELECT DISTINCT P.phone_number
                                         FROM Drivers_License AS D, Persons AS P
                                        WHERE D.car_model='{contact_info["car"]["car_model"]}' AND
                                              D.persons_id=P.id AND
                                              D.car_make='{contact_info["car"]["car_make"]}' AND
                                              D.plate_number='{contact_info["car"]["plate_number"]}' ''')
                rows = cursor.fetchall()
                assert len(rows) > 1, f"Contact information has {len(rows)} for: {database_fn} {contact_info} when expired is not specified"

            # Validate saboteur_info
            with closing(conn.cursor()) as cursor:
                cursor.execute(f'''SELECT count(*)
                                     FROM Parts, Persons
                                    WHERE Persons.id={saboteur_info['id']} AND
                                          Persons.id=Parts.id AND
                                          installed=true''')
                rows = cursor.fetchall()
                assert len(rows) == 1, f"Database {database_fn} saboteur_info has id {saboteur_info['id']} should have one part INSTALLED and it has {len(rows)}"

            gameData[f'{team}{member}'] = dict(database_fn=database_fn,
                                               report_info=report_info,
                                               saboteur_info=saboteur_info,
                                               company_info=company_info,
                                               contact_info=contact_info,
                                            )
            index += 1
    write_schema(gameData)
