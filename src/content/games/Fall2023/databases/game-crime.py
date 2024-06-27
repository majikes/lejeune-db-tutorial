#!/usr/bin/env python3
"""A script to create a sql crime mystery similar to https://mystery.knightlab.com/ """

# pylint: disable=invalid-name
import json
import os
import random
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta

from faker import Faker
from faker_vehicle import VehicleProvider  # pip install faker_vehicle

from COMP421.mypoll.src.config import first_day_of_classes
# Since long text entered, ignore line-too-long pylint warnings along with cursor names
# pylint: disable=line-too-long, redefined-outer-name, invalid-name, too-many-arguments

NUM_TEAMS = 5
NUM_MEMBERS = 4
NUM_DBS = 145
DB_FN = 'sql-murder-mystery.db'
MIN_ADDRESS = 10
MAX_ADDRESS = 1000
MIN_AGE = 16
MAX_AGE = 99
MIN_HEIGHT_MALE = 62
MAX_HEIGHT_MALE = 86
MIN_HEIGHT_FEMALE = 54
MAX_HEIGHT_FEMALE = 74
MEMBERSHIP_STATUSES = ['gold', 'silver', 'platinum']
HAIR_COLOR = ['black', 'brown', 'red', 'blond', 'white']
EYE_COLOR = ['brown', 'hazel', 'green', 'blue', 'grey']

LICENSE_PLATE_PARTIAL_LENGTH = 5
random.seed(0)
Faker.seed(0)
faker = Faker()
faker.add_provider(VehicleProvider)

def sqlite_date(this_date):
    ''' Return the date object in string YYYY-MM-DD format'''
    return this_date.strftime('%Y-%m-%d')

crime_types = ['cyber crime', 'white collar crime', 'embezzlement', 'insurance fraud',
               'money laundering', 'computer crime', 'conspiracy', 'credit fraud',
               'identity theft', 'wire fraud']

street_names = [faker.street_name() for _ in range(NUM_DBS+1)]
assert len(set(street_names)) == NUM_DBS+1

cities = []
while len(cities) < NUM_DBS:
    city = faker.city()
    if city not in cities:
        cities.append(city)
    else:
        print(f'The city {city} appeared twice')
del city # for safety, delete this
assert len(set(cities)) == NUM_DBS

crime_dates = [first_day_of_classes + timedelta(days=2*x) for x in range(NUM_DBS)]
assert len(set(crime_dates)) == NUM_DBS

gym_dates = [crime_dates[x] - timedelta(days=(7+ (x%7))) for x in range(NUM_DBS)]
assert len(gym_dates) == NUM_DBS

male_first_names = [faker.first_name_male() for _ in range((NUM_DBS+1)//2)]
assert len(male_first_names) == (NUM_DBS+1) // 2

female_first_names = [faker.first_name_female() for _ in range((NUM_DBS+1)//2)]
assert len(female_first_names) == (NUM_DBS+1) // 2

last_names = [faker.last_name() for _ in range(NUM_DBS*2)]
assert len(last_names) == 2*NUM_DBS

ssns = [faker.ssn() for _ in range(NUM_DBS)]
assert len(set(ssns)) == NUM_DBS

license_plates = [faker.license_plate() for _ in range(NUM_DBS)]
assert len(set(license_plates)) == NUM_DBS

membership_ids = [faker.bothify(text='??-###') for _ in range(NUM_DBS)]
assert len(set(membership_ids)) == NUM_DBS



def insert_third_witness_interview(cursor, persons_id, guilty_id):
    """ Define the real person who witnessed the crime """
    cursor.execute('''SELECT D.age, D.height_inches, D.eye_color, D.hair_color, D.gender,
                             A.plate_number, A.car_make, A.car_model, A.car_year
                        FROM Driver_licenses as D, Auto_Registrations AS A
                       WHERE D.expired=false AND
                             A.expired=false AND
                             D.persons_id=A.persons_id AND
                             D.persons_id=:guilty_id''',
                   dict(guilty_id=guilty_id))
    car = cursor.fetchone()
    assert car and car['car_make'], f'Database {database} for witness {guilty_id} does not have a valid drivers license'

    cursor.execute('''SELECT I.id
                        FROM interviews I
                       WHERE I.id != :persons_id AND
                             I.id != :guilty_id   ''',
                   dict(persons_id=persons_id, guilty_id=guilty_id))
    interview_ids = cursor.fetchall()
    interview_id = interview_ids[persons_id % len(interview_ids)]['id']

    transcript = f'''I saw the whole thing happen.  The {'guy' if car['gender'] == 'male' else 'lady'} drove away in a {car['car_make']} {car['car_model']} with license plate `{car['plate_number']}`.'''

    third_witness_transcript_query = f'''SELECT P.id, P.name
 FROM Auto_Registrations AS A, Persons as P
  WHERE expired=false AND
        P.id=A.persons_id AND
        A.car_model='{car['car_model']}' AND
        A.car_make='{car['car_make']}' AND
        A.plate_number='{car['plate_number']}' '''

    cursor.execute('''DELETE FROM interviews
                            WHERE id=:interview_id ''',
                   dict(interview_id=interview_id))
    cursor.execute('''INSERT INTO interviews (id, persons_id, transcript)
                           VALUES (:interview_id, :persons_id, :transcript)  ''',
                   dict(interview_id=interview_id, persons_id=persons_id, transcript=transcript))
    return transcript, third_witness_transcript_query


def insert_second_witness_interview(cursor, persons_id, guilty_witness_id):
    """ Define the 'witness' who gives bad testimony.  Is the guilty party """
    cursor.execute('''SELECT D.age, D.height_inches, D.eye_color, D.hair_color, D.gender,
                             A.plate_number, A.car_make, A.car_model, A.car_year
                        FROM Driver_Licenses AS D, Auto_Registrations AS A
                       WHERE D.expired=false AND
                             A.expired=false AND
                             A.persons_id=D.persons_id''')
    cars = cursor.fetchall()

    # Get a unique tuple of eye_color, hair_color, and height_inches
    for offset in range(1, NUM_DBS):
        eyes = dict(eye_color=cars[(persons_id + offset)%len(cars)]['eye_color'],
                    hair_color=cars[(persons_id * offset)%len(cars)]['hair_color'],
                    height_inches=cars[(persons_id - offset)%len(cars)]['height_inches'])
        cursor.execute('''SELECT *
                            FROM Driver_Licenses
                            WHERE eye_color=:eye_color AND
                                  hair_color=:hair_color AND
                                  height_inches=:height_inches ''',
                       eyes)
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            break  # We found a unique combination of eye/hair/height

    # Get a somewhat random interview id
    cursor.execute('''SELECT I.id
                        FROM interviews I
                        WHERE I.id != :persons_id AND
                              I.id != :witness_id   ''',
                   dict(persons_id=persons_id, witness_id=guilty_witness_id))
    interview_ids = cursor.fetchall()
    interview_id = interview_ids[(persons_id * 13) % len(interview_ids)]['id']

    # Get a unique tuple of car_make_car_model, and license plate_number
    for offset in range(1, NUM_DBS):
        plate = dict(plate_number=cars[(persons_id + offset)%len(cars)]['plate_number'],
                     car_make=cars[(persons_id * offset)%len(cars)]['car_make'],
                     car_year=cars[(persons_id * offset)%len(cars)]['car_year'],
                     car_model=cars[(persons_id * offset)%len(cars)]['car_model'])
        cursor.execute('''SELECT *
                            FROM Driver_Licenses as D, Auto_Registrations as A
                           WHERE plate_number=:plate_number AND
                                 car_make=:car_make AND
                                 car_year=:car_year AND
                                 car_model=:car_model ''',
                       plate)
        rows = cursor.fetchall()
        if rows is None or len(rows) == 0:
            break  # We found a unique combination of plate/make/model

    # create a bogus interview
    transcripts = [
        f'''I saw the whole thing.  I took a picture as the guilty person went by the door that had height marks on the frame. The guilty person had {eyes['eye_color']} color eyes, {eyes['hair_color']} hair color, and was exactly {eyes['height_inches']} inches tall.''',
        f'''I saw the whole thing happen. I took a picture as the culpret left in a {plate['car_make']} {plate['car_model']} car with license plate {plate['plate_number']}. ''',
    ]
    transcript = transcripts[persons_id%len(transcripts)]

    second_witness_transcript_queries = [f'''SELECT P.id, P.name
 FROM Driver_Licenses AS D, Persons as P
  WHERE D.height_inches={eyes['height_inches']} AND
         D.eye_color = '{eyes['eye_color']}' AND
         D.hair_color = '{eyes['hair_color']}' AND
         expired=false AND
         P.id = D.persons_id''',
f'''SELECT P.id, P.name
 FROM Auto_Registrations AS A, Persons as P
  WHERE A.car_make='{plate['car_make']}' AND
        A.car_model='{plate['car_model']}' AND
        A.plate_number='{plate['plate_number']}' AND
        expired=false AND
        P.id = A.persons_id''']
    second_witness_transcript_query = second_witness_transcript_queries[persons_id%len(second_witness_transcript_queries)]

    cursor.execute('''DELETE FROM interviews
                             WHERE id=:interview_id ''',
                   dict(interview_id=interview_id))
    cursor.execute('''INSERT INTO interviews (id, persons_id, transcript)
                              VALUES (:interview_id, :persons_id, :transcript)  ''',
                   dict(interview_id=interview_id, persons_id=persons_id, transcript=transcript))
    return transcript, second_witness_transcript_query


def insert_first_witness_interview(cursor, persons_id, guilty_id):
    """ Define the real person who witnessed the crime """
    cursor.execute('''SELECT D.age, D.height_inches, D.eye_color, D.hair_color, D.gender,
                             A.plate_number, A.car_make, A.car_model, A.car_year
                        FROM Driver_licenses as D, Auto_Registrations AS A
                       WHERE D.expired=false AND
                             A.expired=false AND
                             D.persons_id=A.persons_id AND
                             D.persons_id=:guilty_id''',
                   dict(guilty_id=guilty_id))
    car = cursor.fetchone()
    assert car and car['car_make'], f'Database {database} for witness {guilty_id} does not have a valid drivers license'

    cursor.execute('''SELECT I.id
                        FROM interviews I
                       WHERE I.id != :persons_id AND
                             I.id != :guilty_id   ''',
                   dict(persons_id=persons_id, guilty_id=guilty_id))
    interview_ids = cursor.fetchall()
    interview_id = interview_ids[persons_id % len(interview_ids)]['id']

    transcript = f'''I saw the whole thing happen. The {'guy' if car['gender'] == 'male' else 'lady'} was between {car['height_inches'] // 5 * 5} and {car['height_inches'] // 5 * 5 + 5} inches tall, had {car['hair_color']} hair color, {car['eye_color']} eyes, and was about {car['age']} years old.'''

    first_witness_transcript_query = f'''SELECT P.id, P.name
 FROM Driver_Licenses AS D, Persons as P
  WHERE D.gender='{car["gender"]}' AND
               D.height_inches > {car['height_inches'] // 5 * 5} and D.height_inches < {car['height_inches'] // 5 * 5 + 5} AND
               D.hair_color = '{car['hair_color']}' AND
               D.eye_color = '{car['eye_color']}' AND
               D.age = {car['age']} AND
               expired=false AND
               P.id=D.persons_id'''

    cursor.execute('''DELETE FROM interviews
                            WHERE id=:interview_id ''',
                   dict(interview_id=interview_id))
    cursor.execute('''INSERT INTO interviews (id, persons_id, transcript)
                           VALUES (:interview_id, :persons_id, :transcript)  ''',
                   dict(interview_id=interview_id, persons_id=persons_id, transcript=transcript))
    return transcript, first_witness_transcript_query


def insert_random_interview(cursor, index, persons_id=None, transcript=None):
    ''' Create a random transcript to fill out the database'''
    if not persons_id:
        cursor.execute('''SELECT id
                            FROM persons
                           WHERE id not in (SELECT persons_id from interviews)''')
        ids = [row[0] for row in cursor.fetchall()]
        assert len(ids) > 0, 'insert_random_interview found no unused id'
        persons_id = ids[index % len(ids)]

    if not transcript:
        cursor.execute('''SELECT car_make, car_model, plate_number, car_year
                            FROM Auto_Registrations''')
        cars = cursor.fetchall()
        car = cars[index % len(cars)]

        transcripts = [
           f'''I saw the the whole thing happen. The person ran away and jumped into a {car['car_make']} {car['car_model']} with license plate {car['plate_number']}''',
           'I saw the whole thing happen.  The women was dressed in black.  It was Black Widow!!!!',
           'I saw nothing.  Absolutely nothing.',
           f'''I saw the whole thing happen.  The person jumped from a {car['car_make']} {car['car_model']}.  I could only get part of the license plate. It started with {car['plate_number'][:3]}.''',
           f'''I think the car used in the crime had a license plate of {car['plate_number']}''']
        transcript = transcripts[index % len(transcripts)]
        assert  transcript.find("'") == -1, f'Transcript "{transcript}" cannot have a quote in it'

    cursor.execute('''DELETE FROM interviews
                             WHERE persons_id=:persons_id''',
                   dict(persons_id=persons_id))
    cursor.execute('''INSERT INTO interviews (persons_id, transcript)
                              VALUES (:persons_id, :transcript)  ''',
                   dict(persons_id=persons_id, transcript=transcript))


def insert_random_person(cursor, index, street_name=None, address_number=None,
                         ssn=None, first_name=None):
    ''' Create random person info given an index '''
    if not address_number:
        address_number = random.randrange(MIN_ADDRESS, MAX_ADDRESS)
    if index // 2 == 0:
        if not first_name:
            first_name = male_first_names[index//2]
        gender = 'male'
        height = random.randrange(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
    else:
        if not first_name:
            first_name = female_first_names[index//2]
        gender = 'female'
        height = random.randrange(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
    if not ssn:
        ssn = ssns[index]
    name = f'{first_name} {last_names[index]}'
    age = random.randrange(MIN_AGE, MAX_AGE)
    vehicle = faker.vehicle_object()
    eye_color = random.choice(EYE_COLOR) # faker.color_name()
    hair_color = random.choice(HAIR_COLOR) # faker.color_name()
    if not street_name:
        street_name = street_names[index]

    cursor.execute('''DELETE FROM persons  -- ensure unique name/ssn
                            WHERE name=:name OR
                                  ssn=:ssn ''',
                   dict(name=name, ssn=ssn))
    cursor.execute('''INSERT INTO persons (name, address_number, address_street_name, ssn)
                           VALUES (:name, :address_number, :street_name, :ssn)  ''',
                   dict(name=name, address_number=address_number, street_name=street_name, ssn=ssn))
    persons_id = cursor.lastrowid

    # Add drivers license
    if index % 10 == 0:
        # Every ten persons, add an expired drivers license
        cursor.execute('''INSERT INTO Driver_Licenses(persons_id, age, height_inches, eye_color, hair_color,
                                                      gender, expired)
                               VALUES (:persons_id, :age, :height, :eye_color, :hair_color, :gender, 1)''',
                       dict(persons_id=persons_id, age=age, height=height, eye_color=eye_color,
                            hair_color=hair_color, gender=gender))
    cursor.execute('''INSERT INTO Driver_Licenses(persons_id, age, height_inches, eye_color, hair_color,
                                                  gender, expired)
                              VALUES (:persons_id, :age, :height, :eye_color, :hair_color, :gender, 0)''',
                   dict(persons_id=persons_id, age=age, height=height, eye_color=eye_color,
                        hair_color=hair_color, gender=gender))

    # Add a vehicle
    if index % 10 == 0:
        # Every ten persons, add an expired auto registration
        cursor.execute('''INSERT INTO Auto_Registrations (persons_id, expired, plate_number, car_make,
                                                         car_model, car_year)
                                VALUES(:persons_id, 1, :plate_number, :car_make, :car_model, :car_year)''',
                       dict(persons_id=persons_id, plate_number=license_plates[index],
                            car_make=vehicle["Make"], car_model=vehicle["Model"], car_year=vehicle["Year"]))
        vehicle = faker.vehicle_object()
    cursor.execute('''INSERT INTO Auto_Registrations (persons_id, expired, plate_number, car_make,
                                                     car_model, car_year)
                            VALUES(:persons_id, 0, :plate_number, :car_make, :car_model, :car_year)''',
                   dict(persons_id=persons_id, plate_number=license_plates[index],
                        car_make=vehicle["Make"], car_model=vehicle["Model"], car_year=vehicle["Year"]))
    return persons_id


def create_tables(conn, index):
    '''Create a valid reports table in a database
       NOTE: This uses global variables, etc.  Bad.  But a hack to isolate all the noise data
    '''
    report_descriptions = [
        f'Ring doorbell cameras showed two witnesses. The first witness was a man named {male_first_names[3]} who lives on "{street_names[3]}".  The second witness is a woman named {female_first_names[3]} who lives at 721 "{street_names[4]}.',
        'The victim indicated that there were two people present.  The first witness was a UNC professor who was over seven feet tall.   The second witness was a woman who as less than four and a half feet tall.',
        'Security footage showed two witnesses.  The first witness was big and green and had the first name of "Hulk". The second witness had a red, white, and blue shield and everyone seemed to call him "Cap".',
        f'Security footage showed two witnesses. The first witness was a person with last name of {last_names[5]} who lives in {cities[5]}. The second witness is a woman named {female_first_names[3]} with a license of "{license_plates[5]}".',
        'Security footage showed two witnesses come in the door which had height markings.  The first witness was a male that was exactly six feet, two inches tall.   The second witness was a woman who was exactly five feet six inches tall.']

    with closing(conn.cursor()) as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('''CREATE TABLE Reports(
                                        id INTEGER PRIMARY KEY,
                                        crime_date TEXT,   -- 'YYYY-MM-DD'
                                        crime_type TEXT,
                                        description TEXT,
                                        city TEXT);''')
        for csd_index in range(NUM_DBS//2):
            j = index + csd_index
            cursor.execute('''INSERT INTO reports (crime_date, crime_type, description, city)
                                           VALUES(:crime_date, :crime_type, :description, :city)''',
                           dict(crime_date=sqlite_date(crime_dates[j%len(crime_dates)]),
                                crime_type=crime_types[j%len(crime_types)],
                                description=report_descriptions[j%len(report_descriptions)],
                                city=cities[j%len(cities)]))
            cursor.execute('''INSERT INTO reports (crime_date, crime_type, description, city)
                                           VALUES(:crime_date, :crime_type, :description, :city)''',
                           dict(crime_date=sqlite_date(crime_date+timedelta(days=1)),
                                crime_type=crime_type, city=crime_city,
                                description=report_descriptions[j%len(report_descriptions)]))
            cursor.execute('''INSERT INTO reports (crime_date, crime_type, description, city)
                                              VALUES(:crime_date, :crime_type, :description, :city)''',
                           dict(crime_date=sqlite_date(crime_date),
                                crime_type=crime_types[(crime_type_index+1)%len(crime_types)],
                                description=report_descriptions[(index+1)%len(report_descriptions)],
                                city=crime_city))
            cursor.execute('''INSERT INTO reports (crime_date, crime_type, description, city)
                                           VALUES(:crime_date, :crime_type, :description, :city)''',
                           dict(crime_date=sqlite_date(crime_date), crime_type=crime_type,
                                description=report_descriptions[(index+1)%len(report_descriptions)],
                                city=cities[j%len(cities)]))
        conn.commit()

    # create the persons, driver_licenses tables
    with closing(conn.cursor()) as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('''CREATE TABLE Persons(
                                        id INTEGER PRIMARY KEY,
                                        name TEXT,
                                        address_number INTEGER,
                                        address_street_name TEXT,
                                        ssn TEXT)''')
        cursor.execute('''CREATE TABLE Driver_Licenses (
                                        id INTEGER PRIMARY KEY,
                                        persons_id INTEGER,
                                        expired BOOLEAN DEFAULT 0,  -- There are expired driver's licenses
                                        age INTEGER,
                                        height_inches INTEGER,
                                        eye_color TEXT,
                                        hair_color TEXT,
                                        gender TEXT,
                                        CHECK (expired IN (0, 1)),
                                        FOREIGN KEY(persons_id)
                                           REFERENCES Persons(id)
                                           ON DELETE CASCADE)''')
        cursor.execute('''CREATE TABLE Auto_Registrations(
                                        id INTEGER PRIMARY KEY,
                                        persons_id INTEGER,
                                        expired BOOLEAN DEFAULT 0,  -- There  are expired auto registrations
                                        plate_number TEXT,
                                        car_make TEXT,
                                        car_model TEXT,
                                        car_year INTEGER,
                                        CHECK (expired IN (0, 1)),
                                        FOREIGN KEY(persons_id)
                                           REFERENCES Persons(id)
                                           ON DELETE CASCADE)''')

        for j in range(NUM_DBS):
            insert_random_person(cursor, j)
        conn.commit()

    # create the interviews table
    with closing(conn.cursor()) as cursor:
        cursor.execute('PRAGMA foreign_keys = ON')
        cursor.execute('''CREATE TABLE Interviews(
                                        id INTEGER PRIMARY KEY,
                                        persons_id INTEGER,
                                        transcript TEXT NOT NULL,
                                        FOREIGN KEY(persons_id)
                                           REFERENCES Persons(id)
                                           ON DELETE CASCADE)''')

        for j in range(NUM_DBS):
            insert_random_interview(cursor, j)
        conn.commit()

crime_type_index = 0
index = 0
gameData = dict(NUM_TEAMS=NUM_TEAMS, NUM_MEMBERS=NUM_MEMBERS)  # dict indexed by f'{team_number}{member_number}'
for team in range(NUM_TEAMS+1):
    for member in range(NUM_MEMBERS):
        database=f'crime{team}{member}.sqlite'
        crime_type = crime_types[crime_type_index]
        crime_date = crime_dates[index]
        crime_city = cities[index]
        starting_description=f'''A crime has taken place and you as the lead detective must find the crime sceen report, analzye the data, and solve the crime.  Luckily, your department stores all the reports in the database. And you took COMP 421 at UNC so you're excited to show off your skills.  You are told that the crime was a {crime_type} that occurred sometime on {crime_date.strftime('%A, %B %d, %Y')} and that it took place in the city of {crime_city}.

Start by writing a SQL query to retrieve the corresponding crime scene report's id and description from the police department's database.'''
        starting_description_query=f'''
SELECT id, description
  FROM reports
 WHERE crime_type = '{crime_type}' AND
       crime_date = '{sqlite_date(crime_date)}' AND
       city = '{crime_city}'  '''
        starting_description_query = " ".join(starting_description_query.split())   # Remove extra whitespace


        house_location = ['first', 'last'][index %2]
        witness_A_street_name = street_names[index]
        witness_A = f'''lives at the {house_location} house on a street named "{witness_A_street_name}"'''
        witness_A_query = f'''
WITH M as (SELECT {['min', 'max'][index%2]}(address_number) as number
             FROM persons
            WHERE address_street_name = '{street_names[index]}')

SELECT id, name
  FROM persons as P, M
 WHERE P.address_street_name = '{witness_A_street_name}' AND
       P.address_number = M.number '''
        # witness_A_query = " ".join(witness_A_query.split())  # Remove whitespace

        witness_B_first_name = [male_first_names[index // 2], female_first_names[index // 2]][index % 2]
        witness_B_street_name = street_names[index+1]
        witness_B = f'''named {witness_B_first_name} lives somewhere on a street named "{witness_B_street_name}"'''
        witness_B_query = f'''
SELECT id, name
  FROM persons
 WHERE name like '{witness_B_first_name}%' AND
       address_street_name='{witness_B_street_name}' '''
        # witness_B_query = " ".join(witness_B_query.split())  # Remove whitespace

        vehicle = faker.vehicle_object()
        witness_C_car_make = vehicle['Make']
        witness_C_car_model = vehicle['Model']
        witness_C_car_year = vehicle['Year']
        # Faker always makes plate_number's of length 7 or less
        witness_C_plate_number = random.choice(['UNC-Go-Heels', 'COMP-421-DBMA-1', 'DBMA-Rules', 'SQL-Master'])
        witness_C = f'''drove a {witness_C_car_year} {witness_C_car_make} {witness_C_car_model} with license plate '{witness_C_plate_number}' from the scene'''
        witness_C_query = f'''
SELECT P.id, P.name
  FROM Persons AS P, Auto_Registrations AS A
 WHERE P.id=A.persons_id AND
       A.expired=false AND
       ((A.car_make='{witness_C_car_make}' AND
        A.car_model='{witness_C_car_model}' AND
        A.car_year={witness_C_car_year}) OR
        A.plate_number='{witness_C_plate_number}')'''

        crime_description = f'''Security footage shows that there were three witnesses.  The first witness {[witness_A, witness_B, witness_C][index % 3]}. The second witness {[witness_A, witness_B, witness_C][(index+1) % 3]}. And the last witness {[witness_A, witness_B, witness_C][(index+2) % 3]}.'''
        crime_description_index = 2 * team + member + 10


        # Make the database entries
        if os.path.isfile(database):
            os.remove(database)
        conn = sqlite3.connect(database)
        conn.row_factory = sqlite3.Row
        create_tables(conn, index)

        # Insert the correct report
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute('''DELETE FROM reports
                                            WHERE id = :id ''',
                           dict(id=crime_description_index))
            cursor.execute('''DELETE FROM reports
                                           WHERE crime_type=:crime_type AND
                                                 crime_date=:crime_date AND
                                                 city=:city ''',
                           dict(crime_type=crime_type, crime_date=sqlite_date(crime_date), city=crime_city))
            cursor.execute('''INSERT INTO reports (id, crime_date, crime_type, description, city)
                                           VALUES(:id, :crime_date, :crime_type, :description, :city)''',
                           dict(id=crime_description_index, crime_date=sqlite_date(crime_date), crime_type=crime_type,
                                description=crime_description, city=crime_city))
            conn.commit()

        # validate the reports
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute(''' SELECT id, description
                                  FROM reports
                                 WHERE crime_type=:crime_type AND
                                       crime_date=:crime_date AND
                                       city=:city  ''',
                           dict(crime_type=crime_type, crime_date=sqlite_date(crime_date),
                                city=crime_city))
            rows = cursor.fetchall()
            assert len(rows) == 1, f'Crime scene report: index {index} has {len(rows)} rows that match'
            assert rows[0][0] == crime_description_index, f'Crime scene report: index {index} the database index is {rows[0][0]} and should be {crime_description_index}'
            assert rows[0][1] == crime_description, f'Crime scene report: index {index} the database id {crime_description_index} is "{rows[0][1]}" and should be "{crime_description}".'

        # Insert the correct first witness
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            # Make sure there are multiple addresses at street_names[index]
            for i in range(4):
                persons_id = insert_random_person(cursor, i, street_name=witness_A_street_name)
            conn.commit()

            if house_location == 'first':
                f = 'min'
                offset = -10
            else:
                f = 'max'
                offset = 10
            cursor.execute(f'''SELECT {f}(address_number)
                                FROM persons
                               WHERE address_street_name=:address_street_name ''',
                           dict(address_street_name=witness_A_street_name))
            address_number = cursor.fetchone()[0] + offset
            witness_A_id = insert_random_person(cursor, random.randrange(NUM_DBS),
                                                        street_name=witness_A_street_name,
                                                        address_number=address_number)
            conn.commit()

        # Validate witness A
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute(witness_A_query)
            rows = cursor.fetchall()
            assert len(rows) == 1, f'Witness_A_query had {len(rows)} and should have 1'
            witness_A_name = rows[0][1]

        # Insert the correct second witness
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            # Insert another person at that street address but with a different first name
            if index // 2:
                first_name = male_first_names[index//2]
            else:
                first_name = female_first_names[index//2]
            persons_id = insert_random_person(cursor, index,
                                                      street_name=witness_B_street_name,
                                                      ssn=ssns[(index+1)%len(ssns)],
                                                      first_name=first_name)

            # insert witness B
            witness_B_id = insert_random_person(cursor, index,
                                                        street_name=witness_B_street_name,
                                                        first_name=witness_B_first_name)
            conn.commit()

        # Validate witness B
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute(witness_B_query)
            rows = cursor.fetchall()
            assert len(rows) == 1, f'Witness_B_query had {len(rows)} and should have 1'
            assert witness_B_first_name in rows[0][1], f'Witness_B_query had a name of {rows[0][1]} but should have started with {witness_B_first_name}'
            witness_B_name = rows[0][1]

        # Insert the correct third witness
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            persons_id = insert_random_person(cursor, (witness_A_id + witness_B_id) % NUM_DBS)
            # Ensure all witness C's auto's randomly entered are expired
            cursor.execute('''UPDATE Auto_Registrations SET expired=1
                                                  WHERE persons_id=:persons_id OR
                                                        plate_number=:plate_number OR
                                                        (car_make=:car_make AND
                                                         car_model=:car_model AND
                                                         car_year=:car_year)''',
                           dict(persons_id=persons_id, plate_number=witness_C_plate_number,
                                car_make=witness_C_car_make, car_model=witness_C_car_model,
                                car_year=witness_C_car_year))
            cursor.execute('''INSERT INTO Auto_Registrations (persons_id, expired, plate_number, car_make,
                                                              car_model, car_year)
                                                      VALUES (:persons_id, 0, :plate_number, :car_make,
                                                              :car_model, :car_year)''',
                           dict(persons_id=persons_id, plate_number=witness_C_plate_number,
                                car_make=witness_C_car_make,
                                car_model=witness_C_car_model, car_year=witness_C_car_year))
            witness_C_id = persons_id
            conn.commit()

        # Validate third witness interview
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute('''SELECT P.id, P.name
                                FROM Persons AS P, Auto_Registrations AS A
                               WHERE P.id=A.persons_id AND
                                     A.expired=false AND
                                     ((car_make=:car_make AND
                                       car_model=:car_model AND
                                       car_year=:car_year) OR
                                      plate_number=:plate_number)''',
                           dict(car_make=witness_C_car_make, car_model=witness_C_car_model,
                                car_year=witness_C_car_year, plate_number=witness_C_plate_number))
            rows = cursor.fetchall()
            assert len(rows) == 1, f'Database {database} should only have one {witness_C_car_year} {witness_C_car_make} {witness_C_car_model} or a car with plate {witness_C_plate_number}, but has {len(rows)}'
            witness_C_name = rows[0]['name']


        first_witness_id = [witness_A_id, witness_B_id, witness_C_id][index%3]
        first_witness_name = [witness_A_name, witness_B_name, witness_C_name][index%3]
        first_witness_query = [witness_A_query, witness_B_query, witness_C_query][index%3]
        second_witness_id = [witness_A_id, witness_B_id, witness_C_id][(index+1)%3]
        second_witness_name = [witness_A_name, witness_B_name, witness_C_name][(index+1)%3]
        second_witness_query = [witness_A_query, witness_B_query, witness_C_query][(index+1)%3]
        third_witness_id = [witness_A_id, witness_B_id, witness_C_id][(index+2)%3]
        third_witness_name = [witness_A_name, witness_B_name, witness_C_name][(index+2)%3]
        third_witness_query = [witness_A_query, witness_B_query, witness_C_query][(index+2)%3]

        guilty_witness_id = [witness_A_id, witness_B_id, witness_C_id][(index+1)%3]

        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            first_witness_transcript, first_witness_transcript_query = \
                insert_first_witness_interview(cursor, first_witness_id, guilty_witness_id)
            second_witness_transcript, second_witness_transcript_query = \
                insert_second_witness_interview(cursor, second_witness_id, guilty_witness_id)
            third_witness_transcript, third_witness_transcript_query = \
                insert_third_witness_interview(cursor, third_witness_id, guilty_witness_id)
            conn.commit()

        # Validate first witness interview
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            cursor.execute('''SELECT I.id, I.transcript
                                FROM interviews I, persons P
                               WHERE I.persons_id = P.id AND
                                     I.persons_id=:id AND
                                     P.name=:name ''',
                           dict(id=first_witness_id, name=first_witness_name))
            rows = cursor.fetchall()
            assert len(rows) == 1, f'First witness interview had {len(rows)} and should have 1'

            cursor.execute('''SELECT I.id, I.transcript
                                FROM interviews I, persons P
                               WHERE I.persons_id = P.id AND
                                     I.persons_id=:id AND
                                     P.name=:name ''',
                           dict(id=second_witness_id, name=second_witness_name))
            rows = cursor.fetchall()
            assert len(rows) == 1, f'Database {database} second witness interview had {len(rows)} and should have 1'

        # Final validation
        with closing(conn.cursor()) as cursor:
            cursor.execute('PRAGMA foreign_keys = ON')
            for q, i in [(first_witness_query, first_witness_id),
                         (second_witness_query, second_witness_id),
                         (third_witness_query, third_witness_id)]:
                cursor.execute(q)
                rows = cursor.fetchall()
                assert len(rows) == 1, f'Database {database} query "{q}" returned {len(rows)}'
                assert rows[0]['id'] == i, f'Database {database} query "{q}" returned id {rows[0]["id"]} instead of {i}'

        gameData[f'{team}{member}'] = dict(database=database,
                                           starting_description=starting_description,
                                           starting_description_query=starting_description_query,
                                           crime_description=crime_description,
                                           first_witness_id=first_witness_id,
                                           first_witness_name=first_witness_name,
                                           first_witness_query=first_witness_query,
                                           first_witness_transcript=first_witness_transcript,
                                           first_witness_transcript_query=first_witness_transcript_query,
                                           second_witness_id=second_witness_id,
                                           second_witness_name=second_witness_name,
                                           second_witness_query=second_witness_query,
                                           second_witness_transcript=second_witness_transcript,
                                           second_witness_transcript_query=second_witness_transcript_query,
                                           third_witness_id=third_witness_id,
                                           third_witness_name=third_witness_name,
                                           third_witness_query=third_witness_query,
                                           third_witness_transcript=third_witness_transcript,
                                           third_witness_transcript_query=third_witness_transcript_query,
                                           guilty_witness_id=guilty_witness_id)



        index += 1
        crime_type_index = (crime_type_index+1) % len(crime_types)

# Get the schema
conn = sqlite3.connect(database)
conn.row_factory = sqlite3.Row
with closing(conn.cursor()) as cursor:
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('''SELECT sql
                        FROM sqlite_schema
                       WHERE type='table'  ''')
    gameData['schema'] = re.sub("\n  *",
                                "\n     ",
                                "\n".join([x[0] for x in cursor.fetchall()]))

with open('game-crime.json', 'w', encoding='utf-8') as fid:
    json.dump(gameData, fid)



second_query_first_witness = '''
WITH max_num as (SELECT max(address_number) as last
                   FROM person
                  WHERE address_street_name = 'Northwestern Dr')

SELECT * FROM person, max_num
 WHERE address_street_name == 'Northwestern Dr' and
       address_number = max_num.last
'''
# id 14887
# name Morty Schapiro
# license_id 118009
# address_number 4919
# address_street_name Northwestern Dr
# ssn 111564949

second_query_second_witness = '''
SELECT * FROM person
 WHERE name like 'Annabel%' and
       address_street_name = 'Franklin Ave';
'''
# id 16371
# name Annabel Miller
# license_id 49017
# address_number 103
# address_street_name Franklin Ave
# ssn 31871143


Witness_transcript_query = '''
select name, transcript
  from interview I, person P
   where person_id in (14887, 16371) and
          p.id = I.person_id;
'''
# name: Morty Schapiro
# transcript: I heard a gunshot and then saw a man run out. He had a "Get Fit Now Gym" bag. The membership number on the bag started with "48Z". Only gold members have those bags. The man got into a car with a plate that included "H42W".

# name: Annabel Miller
# transcript: I saw the murder happen, and I recognized the killer from my gym when I was working out last week on January the 9th.
