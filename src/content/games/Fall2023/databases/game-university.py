#!/usr/bin/env python3
"""A script to create a sql university database similar to Figure 2.9 of Silberschatz """

# pylint: disable=invalid-name, too-many-locals, too-many-statements, too-many-lines, too-many-branches
import csv
import json
from math import ceil
import os
import random
import re
import sqlite3
from contextlib import closing
from datetime import timedelta, date

from faker import Faker

from COMP421.mypoll.src.config import first_day_of_classes
# Since long text entered, ignore line-too-long pylint warnings along with cursor names
# pylint: disable=line-too-long, redefined-outer-name, invalid-name, too-many-arguments

NUM_MEMBERS = 4
NUM_DBS = 85
NUM_TEAMS = ceil( NUM_DBS / NUM_MEMBERS )
NUM_CLASSROOMS_PER_BUILDING = 5
CLASSROOM_CAPACITY_LIMITS = [30, 475]
STUDENTS_PER_DEPARTMENT = 8
INSTRUCTORS_PER_DEPARTMENT = 5
MIN_ADDRESS = 10
MAX_ADDRESS = 1000
STUDENT_MIN_AGE = 16
STUDENT_MAX_AGE = 26
MIN_HEIGHT_MALE = 62
MAX_HEIGHT_MALE = 86
MIN_HEIGHT_FEMALE = 54
MAX_HEIGHT_FEMALE = 74
THIS_YEAR = date.today().year
THIS_SEMESTER = 'Fall' if 6 < date.today().month < 12 else 'Spring'
HAIR_COLOR = ['black', 'brown', 'red', 'blond', 'white']
EYE_COLOR = ['brown', 'hazel', 'green', 'blue', 'grey', 'amber']
INSTRUCTOR_MIN_SALARY = 65000
INSTRUCTOR_MAX_SALARY = 185000
INSTRUCTOR_MIN_AGE = 27
INSTRUCTOR_MAX_AGE = 79
SECTIONS_PER_COURSE = 4
SEMESTERS = ['Fall', 'Winter', 'Spring', 'Summer']
MIN_SECTION_ID = 1
MAX_SECTION_ID = 3
CORE_COURSES_PER_STUDENT = 2
NON_CORE_COURSES_PER_STUDENT = 2
GRADES = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'F']

COURSE_CSV_FILE = 'game-university.course.csv'
COURSE_COLUMNS = ['course_id', 'title', 'dept_name', 'credits', 'prereqs']
TIME_SLOT_CSV_FILE = 'game-university.time-slot.csv'
TIME_SLOT_COLUMNS = ['time_slot_id', 'day', 'start_hr', 'start_min', 'end_hr', 'end_min']
DEPARTMENT_CSV_FILE = 'game-university.department.csv'
DEPARTMENT_COLUMNS = ['dept_name', 'building', 'budget']
CLASSROOM_BUILDING_CSV_FILE = 'game-university.classroom-building.csv'
CLASSROOM_BUILDING_COLUMNS = [ 'building', 'abbreviation']
OUTPUT_JSON_FILE = 'game-university.json'

random.seed(0)
Faker.seed(0)
faker = Faker()

male_first_names = sorted(set(faker.first_name_male() for _ in range(NUM_DBS*2)))
assert len(male_first_names) >= NUM_DBS // 2  + 10, f'Number of male unique male first names are {len(male_first_names)} NUM_DBS {NUM_DBS}'

female_first_names = sorted(set(faker.first_name_female() for _ in range(NUM_DBS*2)))
assert len(female_first_names) >= NUM_DBS // 2 + 10

last_names = sorted(set(faker.last_name() for _ in range(NUM_DBS*2)))
assert len(last_names) >= NUM_DBS + 10, f'Number of last names is {len(last_names)}, NUM_DBS {NUM_DBS}'

ssns = list(set(faker.ssn() for _ in range(NUM_DBS*200)))
assert len(ssns) >= NUM_DBS + 10, f'Number ssns {len(ssns)}, NUM_DBS {NUM_DBS}'


def getCursor(conn_parm):
    ''' Get the cursor with a foreign_key check ON '''
    ret_cursor = conn_parm.cursor()
    ret_cursor.execute('PRAGMA foreign_keys = ON')
    return ret_cursor

def sqlite_date(this_date):
    ''' Return the date object in string YYYY-MM-DD format'''
    return this_date.strftime('%Y-%m-%d')

dates_of_cheating = [first_day_of_classes + timedelta(days=2*x) for x in range(NUM_DBS)]
assert len(set(dates_of_cheating)) == NUM_DBS

def populate_time_slot_table(conn):
    ''' Read the game-university.time-slot.csv and insert into the time_slot table'''
    with open(TIME_SLOT_CSV_FILE, encoding='utf-8') as csvfile, \
         closing(getCursor(conn)) as cursor:
        reader = csv.reader(csvfile, delimiter=',')
        columns = next(reader)
        assert columns == TIME_SLOT_COLUMNS
        for row in reader:
            cursor.execute("""INSERT INTO time_slot (time_slot_id, day, start_hr, start_min,
                                                     end_hr, end_min)
                                              VALUES (:time_slot_id, :day, :start_hr, :start_min,
                                                      :end_hr, :end_min)""",
                           dict(time_slot_id=row[0],
                                day=row[1],
                                start_hr=row[2],
                                start_min=row[3],
                                end_hr=row[4],
                                end_min=row[5]))
        conn.commit()

def populate_department_table(conn):
    ''' Read the game-university.department.csv and insert into the department table'''
    with open(DEPARTMENT_CSV_FILE, encoding='utf-8') as csvfile, \
         closing(getCursor(conn)) as cursor:
        reader = csv.reader(csvfile, delimiter=',')
        columns = next(reader)
        assert columns == DEPARTMENT_COLUMNS
        for row in reader:
            cursor.execute("""INSERT INTO Department (dept_name, building, budget)
                                              VALUES (:dept_name, :building, :budget)""",
                           dict(dept_name=row[0],
                                building=row[1],
                                budget=row[2]))
        conn.commit()

def populate_classroom_table(conn):
    ''' Read the game-university.classroom-building.csv and insert into the classroom table'''
    with open(CLASSROOM_BUILDING_CSV_FILE, encoding='utf-8') as csvfile, \
         closing(getCursor(conn)) as cursor:
        reader = csv.reader(csvfile, delimiter=',')
        column = next(reader)
        assert column == CLASSROOM_BUILDING_COLUMNS
        for row in reader:
            numbers_for_this_building = []
            for _ in range(NUM_CLASSROOMS_PER_BUILDING):
                room_number = random.randrange(400)
                while room_number in numbers_for_this_building: # room numbers must be unique
                    room_number = random.randrange(400)
                numbers_for_this_building.append(room_number)
                capacity = random.randint(CLASSROOM_CAPACITY_LIMITS[0],
                                          CLASSROOM_CAPACITY_LIMITS[1])
                cursor.execute("""INSERT INTO Classroom (building, room_number, capacity)
                                                 VALUES (:building, :room_number, :capacity)""",
                               dict(building=row[0],
                                    room_number=f'{row[1]} {room_number:0>3}',
                                    capacity=capacity))
        conn.commit()

def populate_course_table(conn):
    ''' Read the game-university.course.csv and insert into the course table'''
    with open(COURSE_CSV_FILE, encoding='utf-8') as csvfile, \
         closing(getCursor(conn)) as cursor:
        reader = csv.reader(csvfile, delimiter=',')
        column = next(reader)
        assert column == COURSE_COLUMNS
        for row in reader:
            if len(row) < 4:
                break
            try:
                cursor.execute("""INSERT INTO Course (course_id, title, dept_name, credits)
                                              VALUES (:course_id, :title, :dept_name, :credits)""",
                               dict(course_id=row[0],
                                    title=row[1],
                                    dept_name=row[2],
                                    credits=row[3]))
            except sqlite3.IntegrityError as e:
                print(row)
                conn.commit()
                raise e
            if len(row) == 5:  # Be forgiving if no comma to designate no prereqs
                for prereq in row[4].split(','):
                    prereq = prereq.strip()
                    if len(prereq) == 0:
                        continue
                    try:
                        cursor.execute("""INSERT INTO Prereq (course_id, prereq_id)
                                                      VALUES (:course_id, :prereq_id)""",
                                       dict(course_id=row[0],
                                            prereq_id=prereq))
                    except sqlite3.IntegrityError as e:
                        print(row, prereq)
                        conn.commit()
                        raise e
        conn.commit()

def get_advocate_id(index):
    ''' standardize advocate id'''
    return f'10{(index+37)%1000:03d}'

def get_accused_id(index):
    ''' standardize accused id'''
    return f'1{(index+37)%1000:03d}0'

def get_teacher_id(index):
    ''' standardize teacher id '''
    return f'1{(index+37)%1000:03d}1'

def get_id_candidates(cursor, index):
    ''' utility to get all the possible IDs available'''
    cursor.execute("""SELECT ID from id_card order by ID""")
    candidates = set(f'{x}' for x in range(0,100000))
    candidates = candidates - set(row[0] for row in cursor.fetchall()) - set([get_advocate_id(index),
                                                                              get_accused_id(index),
                                                                              get_teacher_id(index)])
    return list(candidates)

def get_advocate_ssn(index):
    '''standardize advocate ssn'''
    return f'202-52-1{(index+37)%1000:03d}'

def get_accused_ssn(index):
    '''standardize accused ssn'''
    return f'522-02-2{(index+37)%1000:03d}'

def get_teacher_ssn(index):
    '''standardize teacher ssn'''
    return f'533-02-3{(index+37)%1000:03d}'

def get_ssn_candidates(cursor, index):
    ''' utility to get all the possible ssns available
    Exclude the one used for the advocate, the accussed, and the professor'''
    cursor.execute("""SELECT ssn from id_card order by ID""")
    candidates = set(ssns) - set(row[0] for row in cursor.fetchall()) - set([get_advocate_ssn(index),
                                                                             get_accused_ssn(index),
                                                                             get_teacher_ssn(index)])
    return list(candidates)

def get_dept_names(cursor):
    ''' Get the list of department name '''
    cursor.execute("""SELECT dept_name FROM department""")
    return [x[0] for x in cursor.fetchall()]

def populate_student_table(conn, index):
    ''' populate the student (and id_card) table with about STUDENTS_PER_DEPARTMENT students'''
    name_counter = 0

    with closing(getCursor(conn)) as cursor:

        candidates = get_id_candidates(cursor, index)
        ssn_candidates = get_ssn_candidates(cursor, index)

        for i, dept_name in enumerate(get_dept_names(cursor)):
            students_per_department = STUDENTS_PER_DEPARTMENT + ((index + i) % 4)
            for i in range(students_per_department):
                # Get possible id numbers
                s_id = random.choices(candidates, k=1)[0]
                del candidates[candidates.index(s_id)]

                if i // 2 == 0:
                    gender = 'male'
                    name = f'{random.choices(male_first_names, k=1)[0]} {random.choices(last_names, k=1)[0]}'
                    height = random.randint(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
                else:
                    gender = 'female'
                    name = f'{random.choices(female_first_names, k=1)[0]} {random.choices(last_names, k=1)[0]}'
                    height = random.randint(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
                eye_color = random.choice(EYE_COLOR)
                hair_color = random.choice(HAIR_COLOR)
                ssn = random.choices(ssn_candidates, k=1)[0]
                del ssn_candidates[ssn_candidates.index(ssn)]
                dob = faker.date()
                dob = f'{date.today().year - random.randint(STUDENT_MIN_AGE, STUDENT_MAX_AGE)}-{dob[5:]}'
                name_counter += 1

                try:
                    sql_parm = dict(id=s_id,
                                    name=name,
                                    dob=dob,
                                    height_inches=height,
                                    eye_color=eye_color,
                                    hair_color=hair_color,
                                    ssn=ssn,
                                    gender=gender)
                    cursor.execute("""INSERT INTO id_card (ID, name, DOB, height_inches, ssn,
                                                          eye_color, hair_color, gender)
                                                  VALUES (:id, :name, :dob, :height_inches, :ssn,
                                                          :eye_color, :hair_color, :gender)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm, '\n', e)
                    conn.commit()
                    raise e
                try:
                    sql_parm = dict(id=s_id,
                                    dept_name=dept_name,
                                    tot_cred=random.randint(0, 124))
                    cursor.execute("""INSERT INTO student (ID, dept_name, tot_cred)
                                                  VALUES (:id, :dept_name, :tot_cred)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm)
                    conn.commit()
                    raise e
        conn.commit()

def populate_instructor_table(conn, index):
    ''' populate the instructor, id_card, and advisee table with about INSTRUCTORS_PER_DEPARTMENT students'''
    name_counter = 0

    with closing(getCursor(conn)) as cursor:

        cursor.execute("""SELECT I.ID from id_card I, student S WHERE S.ID=I.ID""")
        student_ids = set(row[0] for row in cursor.fetchall())

        candidates = get_id_candidates(cursor, index)
        ssn_candidates = get_ssn_candidates(cursor, index)

        for i, dept_name in enumerate(get_dept_names(cursor)):
            instructors_per_department = INSTRUCTORS_PER_DEPARTMENT + ((index + i) % 3)
            for i in range(instructors_per_department):
                # Get possible id numbers
                i_id = random.choices(candidates, k=1)[0]
                del candidates[candidates.index(i_id)]

                if i // 2 == 0:
                    gender = 'male'
                    name = f'{random.choices(male_first_names, k=1)[0]} {random.choices(last_names, k=1)[0]}'
                    height = random.randint(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
                else:
                    gender = 'female'
                    name = f'{random.choices(female_first_names, k=1)[0]} {random.choices(last_names, k=1)[0]}'
                    height = random.randint(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
                eye_color = random.choice(EYE_COLOR)
                hair_color = random.choice(HAIR_COLOR)
                ssn = random.choices(ssn_candidates, k=1)[0]
                del ssn_candidates[ssn_candidates.index(ssn)]
                dob = faker.date()
                dob = f'{date.today().year - random.randint(INSTRUCTOR_MIN_AGE, INSTRUCTOR_MAX_AGE)}-{dob[5:]}'
                name_counter += 1

                try:
                    sql_parm = dict(id=i_id,
                                    name=name,
                                    dob=dob,
                                    height_inches=height,
                                    eye_color=eye_color,
                                    hair_color=hair_color,
                                    ssn=ssn,
                                    gender=gender)
                    cursor.execute("""INSERT INTO id_card (ID, name, DOB, height_inches, ssn,
                                                          eye_color, hair_color, gender)
                                                  VALUES (:id, :name, :dob, :height_inches, :ssn,
                                                          :eye_color, :hair_color, :gender)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm, '\n', e)
                    conn.commit()
                    raise e

                # Add the instructor
                try:
                    sql_parm = dict(id=i_id,
                                    dept_name=dept_name,
                                    salary=random.randint(INSTRUCTOR_MIN_SALARY, INSTRUCTOR_MAX_SALARY))
                    cursor.execute("""INSERT INTO instructor (ID, dept_name, salary)
                                                  VALUES (:id, :dept_name, :salary)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm)
                    conn.commit()
                    raise e

                # Add an advisee
                try:
                    s_id = random.choices(list(student_ids), k=1)[0]
                    student_ids -= {s_id}

                    sql_parm = dict(s_id=s_id,
                                    i_id=i_id)
                    cursor.execute("""INSERT INTO advisor (s_id, i_id)
                                                  VALUES (:s_id, :i_id) """,
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm)
                    conn.commit()
                    raise e
        conn.commit()

def populate_teaches_table(conn, index):
    ''' populate the teaches and the section table'''

    with closing(getCursor(conn)) as cursor:

        cursor.execute("""SELECT building, room_number FROM classroom""")
        class_building_room = [(row[0], row[1]) for row in cursor.fetchall()]

        cursor.execute("""SELECT DISTINCT time_slot_id FROM time_slot""")
        time_slot_ids = [row[0] for row in cursor.fetchall()]

        for i, dept_name in enumerate(get_dept_names(cursor)):

            cursor.execute("""SELECT ID from instructor where dept_name=:dept_name""",
                           dict(dept_name=dept_name))
            instructors = [row[0] for row in cursor.fetchall()]

            cursor.execute("""SELECT course_id FROM course where dept_name=:dept_name""",
                           dict(dept_name=dept_name))
            course_ids = [row[0] for row in cursor.fetchall()]

            sections_added_so_far = []

            sections_per_course = SECTIONS_PER_COURSE + ((index + i) % 3)
            for _ in range(sections_per_course):
                # Get possible id numbers
                course_id = random.choices(course_ids, k=1)[0]
                instructor_id = random.choices(instructors, k=1)[0]
                if len(sections_added_so_far) == 0:
                    # Ensure that there are courses taught this semester/year
                    semester = THIS_SEMESTER
                    year = THIS_YEAR
                else:
                    semester = random.choices(SEMESTERS, k=1)[0]
                    year = random.randint(THIS_YEAR-10, THIS_YEAR)
                building, room_number = random.choices(class_building_room, k=1)[0]
                time_slot_id = random.choices(time_slot_ids, k=1)[0]
                sec_id = random.randint(MIN_SECTION_ID, MAX_SECTION_ID)

                # Ensure Section table primary key not violated
                while (course_id, sec_id, semester, year) in sections_added_so_far:
                    sec_id += 1
                sections_added_so_far.append((course_id, sec_id, semester, year))

                sql_parm = dict(course_id=course_id,
                                sec_id=sec_id,
                                semester=semester,
                                year=year,
                                building=building,
                                room_number=room_number,
                                time_slot_id=time_slot_id,
                                instructor_id=instructor_id)
                try:
                    cursor.execute("""INSERT INTO section (course_id, sec_id, semester, year,
                                                           building, room_number, time_slot_id)
                                                  VALUES (:course_id, :sec_id, :semester, :year,
                                                          :building, :room_number, :time_slot_id)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm, '\n', e)
                    conn.commit()
                    raise e

                # Add the instructor
                try:
                    cursor.execute("""INSERT INTO teaches (id, course_id, sec_id, semester, year)
                                                  VALUES (:instructor_id, :course_id, :sec_id,
                                                          :semester, :year)""",
                                   sql_parm)
                except sqlite3.IntegrityError as e:
                    print(sql_parm)
                    conn.commit()
                    raise e
        conn.commit()

def populate_takes_table(conn, index):
    ''' populate the takes table and add some conversations'''

    with closing(getCursor(conn)) as cursor:

        for i, dept_name in enumerate(get_dept_names(cursor)):

            cursor.execute("""SELECT DISTINCT C.course_id
                                FROM course C, section S
                               WHERE dept_name=:dept_name AND
                                     C.course_id=S.course_id""",
                           dict(dept_name=dept_name))
            core_course_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute("""SELECT C.course_id
                                FROM course C, section S
                               WHERE dept_name!=:dept_name AND
                                     C.course_id=S.course_id""",
                           dict(dept_name=dept_name))
            non_core_course_ids = [row[0] for row in cursor.fetchall()]

            cursor.execute("""SELECT id FROM student where dept_name=:dept_name""",
                           dict(dept_name=dept_name))
            student_ids = [row[0] for row in cursor.fetchall()]

            core_courses_per_student = CORE_COURSES_PER_STUDENT + ((index + i) % 3)
            non_core_courses_per_student = NON_CORE_COURSES_PER_STUDENT + ((index + i) % 2)
            for student_id in student_ids:

                core_courses_remaining = core_course_ids.copy()
                for _ in range(min(core_courses_per_student, len(core_courses_remaining))):
                    course_id = random.choices(core_courses_remaining, k=1)[0]
                    core_courses_remaining.pop(core_courses_remaining.index(course_id))
                    cursor.execute("""SELECT sec_id, semester, year FROM section WHERE course_id=:course_id""",
                                   dict(course_id=course_id))
                    take_info = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
                    sec_id, semester, year = random.choices(take_info, k=1)[0]
                    grade = random.choices(GRADES, k=1)[0]

                    sql_parm = dict(id=student_id,
                                    course_id=course_id,
                                    sec_id=sec_id,
                                    semester=semester,
                                    year=year,
                                    grade=grade)
                    try:
                        cursor.execute("""INSERT INTO takes (id, course_id, sec_id, semester,
                                                             year, grade)
                                                      VALUES (:id, :course_id, :sec_id, 
                                                              :semester, :year, :grade)""",
                                       sql_parm)
                    except sqlite3.IntegrityError as e:
                        print(sql_parm)
                        conn.commit()
                        raise e

                non_core_courses_remaining = non_core_course_ids.copy()
                for _ in range(min(non_core_courses_per_student, len(non_core_courses_remaining))):
                    course_id = random.choices(non_core_courses_remaining, k=1)[0]
                    del non_core_courses_remaining[non_core_courses_remaining.index(course_id)]
                    while course_id in non_core_courses_remaining:
                        # I have no idea why I have to do this!
                        non_core_courses_remaining.pop(non_core_courses_remaining.index(course_id))
                    cursor.execute("""SELECT sec_id, semester, year FROM section WHERE course_id=:course_id""",
                                   dict(course_id=course_id))
                    take_info = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
                    sec_id, semester, year = random.choices(take_info, k=1)[0]
                    grade = random.choices(GRADES, k=1)[0]

                    sql_parm = dict(id=student_id,
                                    course_id=course_id,
                                    sec_id=sec_id,
                                    semester=semester,
                                    year=year,
                                    grade=grade)
                    try:
                        cursor.execute("""INSERT INTO takes (id, course_id, sec_id, semester,
                                                             year, grade)
                                                      VALUES (:id, :course_id, :sec_id, 
                                                              :semester, :year, :grade)""",
                                       sql_parm)
                    except sqlite3.IntegrityError as e:
                        print(sql_parm)
                        conn.commit()
                        raise e

                # Put some conversations in the database
                for s_index, s_id in enumerate(student_ids):
                    if semester == 'Spring':
                        what_date = f'{year}-01-27'
                    elif semester == 'Summer':
                        what_date = f'{year}-06-13'
                    elif semester == 'Winter':
                        what_date = f'{year}-12-08'
                    elif semester == 'Fall':
                        what_date = f'{year}-09-03'
                    what_time = f'09:{(s_index+12)%60}'

                    if index % 3:
                        ids = [s_id, student_ids[(s_index+1)%len(student_ids)],
                               student_ids[(s_index+5)%len(student_ids)]]
                    else:
                        ids = [s_id, student_ids[(s_index+1)%len(student_ids)]]
                    insert_conversation(cursor, what_date, what_time, faker.paragraph(), ids)

        conn.commit()

def populate_tables(conn, index):
    ''' Given a database, fill up the tables '''

    populate_time_slot_table(conn)
    populate_department_table(conn)
    populate_classroom_table(conn)
    populate_course_table(conn)
    populate_student_table(conn, index)
    populate_instructor_table(conn, index)
    populate_teaches_table(conn, index)
    populate_takes_table(conn, index)

def create_tables(conn):
    '''Create a valid reports table in a database
       NOTE: This uses global variables, etc.  Bad.  But a hack to isolate all the noise data
    '''

    with closing(getCursor(conn)) as cursor:
        cursor.execute("""create table classroom
                                       (building     varchar(15),
                                        room_number  varchar(7),
                                        capacity     numeric(4,0),
                                        primary key (building, room_number)
                                       )""")

        cursor.execute("""create table department
                                      (dept_name   varchar(20),
                                       building    varchar(15),
                                       budget      numeric(12,2) check (budget > 0),
                                       primary key (dept_name)
                                      )""")

        cursor.execute("""create table course
                                     (course_id   varchar(8),
                                      title       varchar(50),
                                      dept_name   varchar(20),
                                      credits     numeric(2,0) check (credits > 0),
                                      primary key (course_id),
                                      foreign key (dept_name) references department (dept_name)
                                         on delete set null
                                     )""")
        cursor.execute("""CREATE INDEX idx_course_dept_name ON Course(dept_name)""")

        cursor.execute("""create table instructor
                                     (ID          varchar(5), --- Instructor name in id_card table
                                      dept_name   varchar(20),
                                      salary      numeric(8,2) check (salary > 29000),
                                      primary key (ID),
                                      foreign key (ID) references id_card(id)
                                         on delete cascade,
                                      foreign key (dept_name) references department (dept_name)
                                         on delete set null
                                     )""")
        cursor.execute("""CREATE INDEX idx_instructor_id ON Instructor(ID)""")
        cursor.execute("""CREATE INDEX idx_instructor_dept_name ON Instructor(dept_name)""")

        cursor.execute("""create table section
                                     (course_id    varchar(8),
                                      sec_id       varchar(8),
                                      semester     varchar(6)
                                         check (semester in ('Fall', 'Winter', 'Spring', 'Summer')),
                                      year         numeric(4,0) check (year > 1701 and year < 2024),
                                      building     varchar(15),
                                      room_number  varchar(7),
                                      time_slot_id varchar(4),
                                      primary key (course_id, sec_id, semester, year),
                                      foreign key (course_id) references course (course_id)
                                         on delete cascade,
                                      foreign key (building, room_number) references classroom (building, room_number)
                                         on delete set null
                                     )""")
        cursor.execute("""CREATE INDEX idx_section_year ON Section(year)""")
        cursor.execute("""CREATE INDEX idx_section_semester ON Section(semester)""")

        cursor.execute("""create table teaches
                                     (ID         varchar(5),  -- instructor's ID
                                      course_id  varchar(8),
                                      sec_id     varchar(8),
                                      semester   varchar(6),
                                      year       numeric(4,0),
                                      primary key (ID, course_id, sec_id, semester, year),
                                      foreign key (course_id, sec_id, semester, year)
                                         references section (course_id, sec_id, semester, year)
                                         on delete cascade,
                                      foreign key (ID) references instructor (ID)
                                         on delete cascade
                                     )""")
        cursor.execute("""CREATE INDEX idx_teaches_id ON Teaches(ID)""")
        cursor.execute("""CREATE INDEX idx_teaches_year ON Teaches(year)""")
        cursor.execute("""CREATE INDEX idx_teaches_semester ON Teaches(semester)""")

        cursor.execute("""create table id_card
                                     (ID         varchar(5) PRIMARY KEY,
                                     name        varchar(20) not null,
                                     DOB         date,
                                     expired     Boolean default 0,
                                     height_inches integer,
                                     eye_color   text,
                                     hair_color text,
                                     gender text,
                                     ssn text,
                                     CHECK (expired IN (0, 1))
                                     ) """)
        cursor.execute("""CREATE UNIQUE INDEX idx_id_card_id on id_card(id)""")

        cursor.execute("""create table student
                                     (ID         varchar(5),  -- Student name is in id_card table
                                      dept_name  varchar(20),
                                      tot_cred   numeric(3,0) check (tot_cred >= 0),
                                      primary key (ID),
                                      foreign key (dept_name) references department (dept_name)
                                         on delete set null,
                                      foreign key (ID) references id_card(id)
                                         on delete cascade
                                     )""")
        cursor.execute("""CREATE UNIQUE INDEX idx_student_id ON Student(ID)""")
        cursor.execute("""CREATE INDEX idx_student_dept_name ON Student(dept_name)""")

        cursor.execute("""create table takes
                                     (ID         varchar(5), -- Student ID
                                      course_id  varchar(8),
                                      sec_id     varchar(8),
                                      semester   varchar(6),
                                      year       numeric(4,0),
                                      grade      varchar(2),
                                      primary key (ID, course_id, sec_id, semester, year),
                                      foreign key (course_id, sec_id, semester, year)
                                         references section (course_id, sec_id, semester, year)
                                         on delete cascade,
                                      foreign key (ID) references student (ID)
                                         on delete cascade
                                     )""")
        cursor.execute("""CREATE INDEX idx_takes_id ON Takes(ID)""")
        cursor.execute("""CREATE INDEX idx_takes_semester ON Takes(semester)""")
        cursor.execute("""CREATE INDEX idx_takes_year ON Takes(year)""")

        cursor.execute("""create table advisor
                                     (s_ID       varchar(5),
                                      i_ID       varchar(5),
                                      primary key (s_ID),
                                      foreign key (i_ID) references instructor (ID)
                                         on delete set null,
                                      foreign key (s_ID) references student (ID)
                                         on delete cascade
                                     )""")
        cursor.execute("""CREATE INDEX idx_advisor_instructor_id ON Advisor(i_ID)""")

        cursor.execute("""create table time_slot
                                     (time_slot_id   varchar(4),
                                      day            varchar(1),
                                      start_hr       numeric(2) check (start_hr >= 0 and start_hr < 24),
                                      start_min      numeric(2) check (start_min >= 0 and start_min < 60),
                                      end_hr         numeric(2) check (end_hr >= 0 and end_hr < 24),
                                      end_min        numeric(2) check (end_min >= 0 and end_min < 60),
                                      primary key (time_slot_id, day, start_hr, start_min)
                                     )""")

        cursor.execute("""create table prereq
                                     (course_id      varchar(8),
                                      prereq_id      varchar(8),
                                      primary key (course_id, prereq_id),
                                      foreign key (course_id) references course (course_id)
                                         on delete cascade,
                                      foreign key (prereq_id) references course (course_id)
                                     )""")

        cursor.execute("""create table transcription
                                     (transcription_id integer primary key autoincrement,
                                      what_date         date,
                                      what_time        time,
                                      conversation     text
                                     )""")

        cursor.execute("""create table conversation_participants
                                     (transcription_id  integer,
                                      id                varchar(8),
                                      primary key (transcription_id, id),
                                      foreign key (id) references id_card(id)
                                          on delete set null
                                     )""")
    conn.commit()

def get_student_advocate(conn, index):
    ''' Get the student advocating for the accused.
        The student advocate should be a fixed name because if the database is regenerated, we don't want
        the actual worksheets (which can be hardcoded from the description) to change.
        Return a dictionary of information about the student '''

    with closing(getCursor(conn)) as cursor:
        s_id = get_advocate_id(index)
        dept_name = random.choices(get_dept_names(cursor), k=1)[0]

        last_name = last_names[index % len(last_names)]
        ssn = get_advocate_ssn(index)
        if index // 2 == 0:
            gender = 'male'
            pronoun = 'he'
            possessive_pronoun = 'his'
            first_name = male_first_names[-(index + 1) % len(male_first_names)]
            height = random.randint(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
        else:
            gender = 'female'
            pronoun = 'she'
            possessive_pronoun = 'her'
            first_name = female_first_names[-(index + 1) % len(male_first_names)]
            height = random.randint(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
        name = f'{first_name} {last_name}'
        eye_color = random.choice(EYE_COLOR)
        hair_color = random.choice(HAIR_COLOR)
        dob = faker.date()
        dob = f'{date.today().year - random.randint(STUDENT_MIN_AGE, STUDENT_MAX_AGE)}-{dob[5:]}'

        student_advocate = dict(id=s_id,
                                last_name=last_name,
                                first_name=first_name,
                                name=name,
                                dob=dob,
                                height_inches=height,
                                eye_color=eye_color,
                                hair_color=hair_color,
                                ssn=ssn,
                                gender=gender,
                                pronoun=pronoun,
                                possessive_pronoun=possessive_pronoun,
                                dept_name=dept_name,
                                tot_cred=random.randint(0, 124))
        cursor.execute("""DELETE FROM Id_card WHERE name =:name OR
                                                    ssn = :ssn OR
                                                    id = :id""",
                       student_advocate)
        try:
            cursor.execute("""INSERT INTO id_card (ID, name, DOB, height_inches, ssn,
                                                   eye_color, hair_color, gender)
                                           VALUES (:id, :name, :dob, :height_inches, :ssn,
                                                   :eye_color, :hair_color, :gender)""",
                           student_advocate)
        except sqlite3.IntegrityError as e:
            print(student_advocate, '\n', e)
            conn.commit()
            raise e
        try:
            cursor.execute("""INSERT INTO student (ID, dept_name, tot_cred)
                                           VALUES (:id, :dept_name, :tot_cred)""",
                          student_advocate)
        except sqlite3.IntegrityError as e:
            print(student_advocate, '\n', e)
            conn.commit()
            raise e
        conn.commit()

        return student_advocate

def get_accused_student(conn, index, gd):
    ''' Get the student accused of cheating.
    The accused student should be a fixed name because if the database is regenerated, we don't want
    the actual worksheets (which can be hardcoded from the description) to change.
    Return a dictionary of the student information '''

    with closing(getCursor(conn)) as cursor:
        s_id = get_accused_id(index)
        dept_name = random.choices(get_dept_names(cursor), k=1)[0]

        last_name = last_names[-(index+1) % len(last_names)]
        assert last_name != gd['student_advocate']['last_name'], f'For index={index}, len(last_names)={len(last_names)}, accused and advocate last name is "{last_name}"\n{last_names}' # Check just to make sure unique names

        ssn = get_accused_ssn(index)
        if index // 2 == 1:
            gender = 'male'
            pronoun = 'he'
            possessive_pronoun = 'his'
            first_name = male_first_names[index % len(male_first_names)]
            height = random.randint(MIN_HEIGHT_MALE, MAX_HEIGHT_MALE)
        else:
            gender = 'female'
            pronoun = 'she'
            possessive_pronoun = 'her'
            first_name = female_first_names[index % len(female_first_names)]
            height = random.randint(MIN_HEIGHT_FEMALE, MAX_HEIGHT_FEMALE)
        name = f'{first_name} {last_name}'
        eye_color = random.choice(EYE_COLOR)
        hair_color = random.choice(HAIR_COLOR)
        dob = faker.date()
        dob = f'{date.today().year - random.randint(STUDENT_MIN_AGE, STUDENT_MAX_AGE)}-{dob[5:]}'

        accused_student = dict(id=s_id,
                               last_name=last_name,
                               first_name=first_name,
                               name=name,
                               dob=dob,
                               height_inches=height,
                               eye_color=eye_color,
                               hair_color=hair_color,
                               ssn=ssn,
                               gender=gender,
                               pronoun=pronoun,
                               possessive_pronoun=possessive_pronoun,
                               dept_name=dept_name,
                               tot_cred=random.randint(0, 124))
        cursor.execute("""DELETE FROM Id_card WHERE name = :name OR
                                                    ssn = :ssn OR
                                                    id = :id""",
                       accused_student)
        try:
            cursor.execute("""INSERT INTO id_card (ID, name, DOB, height_inches, ssn,
                                                   eye_color, hair_color, gender)
                                           VALUES (:id, :name, :dob, :height_inches, :ssn,
                                                   :eye_color, :hair_color, :gender)""",
                           accused_student)
        except sqlite3.IntegrityError as e:
            print(accused_student, '\n', e)
            conn.commit()
            raise e
        try:
            cursor.execute("""INSERT INTO student (ID, dept_name, tot_cred)
                                           VALUES (:id, :dept_name, :tot_cred)""",
                          accused_student)
        except sqlite3.IntegrityError as e:
            print(accused_student, '\n', e)
            conn.commit()
            raise e
        conn.commit()

        return accused_student

def get_course_with_accused_advocate(conn, gd):
    ''' Ensure that the accused and the advocate are in a shared course '''
    with open(COURSE_CSV_FILE, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        column = next(reader)
        assert column == COURSE_COLUMNS
        rows = list(reader)
        row = rows[index % len(rows)]

        course = dict(course_id=row[0],
                      title=row[1],
                      dept_name=row[2],
                      credits=row[3],
                      sec_id=1,
                      year=THIS_YEAR,
                      semester=THIS_SEMESTER)

    with open(TIME_SLOT_CSV_FILE, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        column = next(reader)
        assert column == TIME_SLOT_COLUMNS
        rows = list(reader)
        row = rows[index % len(rows)]

        course.update(dict(time_slot_id=row[0],
                           day=row[1],
                           start_hr=row[2],
                           start_min=row[3],
                           end_hr=row[4],
                           end_min=row[5]))

    with closing(getCursor(conn)) as cursor:

        # Select an instructor from the course's department
        cursor.execute("""SELECT I.ID, C.name, C.DOB, C.height_inches,
                                 C.eye_color, C.hair_color, C.gender, I.salary
                            FROM Instructor I, Id_card C
                           WHERE I.dept_name=:dept_name AND
                                 I.ID = C.ID""",
                       course)
        rows = cursor.fetchall()
        row = rows[index % len(rows)]
        old_teacher_id, teacher_name, teacher_gender, teacher_salary = row[0], row[1], row[6], row[7]
        new_teacher_id = get_teacher_id(index)
        new_teacher_ssn = get_teacher_ssn(index)
        if teacher_gender == 'male':
            teacher_pronoun = 'he'
            teacher_possessive_pronoun = 'his'
        else:
            teacher_pronoun = 'she'
            teacher_possessive_pronoun = 'her'
        # Make a new id_card for the teacher
        cursor.execute("""INSERT INTO Id_card (id, name, DOB, height_inches, eye_color, hair_color, gender, ssn)
                                      VALUES(:id, :name, :DOB, :height_inches, :eye_color, :hair_color, :gender, :ssn)""",
                       dict(id=new_teacher_id,
                            name=teacher_name,
                            DOB=row[2],
                            height_inches=row[3],
                            eye_color=row[4],
                            hair_color=row[5],
                            gender=teacher_gender,
                            ssn=new_teacher_ssn))
        # Ensure that the teacher has a standardized SSN
        cursor.execute("""INSERT INTO Instructor (ID, dept_name, salary)
                                         VALUES (:id, :dept_name, :salary)""",
                       dict(id=new_teacher_id,
                            dept_name=course['dept_name'],
                            salary=teacher_salary))
        cursor.execute("""UPDATE Teaches set id=:new_id where id=:old_id""",
                       dict(new_id=new_teacher_id,
                            old_id=old_teacher_id))
        cursor.execute("""DELETE FROM Instructor WHERE id=:id""",
                       dict(id=old_teacher_id))
        cursor.execute("""UPDATE Id_card set expired=1 where id=:id""",
                       dict(id=old_teacher_id))
        course.update(dict(teacher_name=teacher_name,
                           teacher_last_name = teacher_name.split(' ')[-1],
                           teacher_id=new_teacher_id,
                           teacher_ssn=new_teacher_ssn,
                           teacher_gender=teacher_gender,
                           teacher_pronoun=teacher_pronoun,
                           teacher_possesive_pronoun=teacher_possessive_pronoun))

        # Select a building and room
        cursor.execute("""SELECT building, room_number FROM classroom""")
        rows = cursor.fetchall()
        building, room_number = rows[index % len(rows)]
        course.update(dict(building=building,
                           room_number=room_number))

        # Make sure there is no other course at this time and section
        cursor.execute("""DELETE FROM section WHERE course_id = :course_id AND
                                                    sec_id = :sec_id AND
                                                    semester = :semester AND
                                                    year = :year""",
                       course)

        cursor.execute("""INSERT INTO section (course_id, sec_id, semester, year,
                                                             building, room_number, time_slot_id)
                                                    VALUES (:course_id, :sec_id, :semester, :year,
                                                            :building, :room_number, :time_slot_id)""",
                                     course)


        # Ensure the teacher teaches that course, section
        cursor.execute("""INSERT INTO Teaches (id, course_id, sec_id, semester, year)
                                      VALUES (:teacher_id, :course_id, :sec_id, :semester, :year)""",
                       course)

        # Ensure that both students are taking this course
        for s_id in [gd['student_advocate']['id'], gd['accused_student']['id']]:
            course['id'] = s_id
            try:
                cursor.execute("""INSERT INTO takes (id, course_id, sec_id, semester,
                                                     year, grade)
                                              VALUES (:id, :course_id, :sec_id,
                                                      :semester, :year, Null)""",
                               course)
            except sqlite3.IntegrityError as e:
                if s_id == gd['student_advocate']['id']:
                    print('student advocate')
                else:
                    print('accused student')
                print(course)
                conn.commit()
                raise e
        del course['id']

        # Ensure that no one in this course, this semester, this year has a grade yet
        try:
            cursor.execute("""Update Takes set grade=Null
                                     WHERE course_id=:course_id AND
                                           sec_id=:sec_id AND
                                           semester=:semester AND
                                           year=:year """,
                           course)
        except sqlite3.IntegrityError as e:
            print(course)
            conn.commit()
            raise e

        # Insert a innoculous conversation
        conversation = f'''Hi, {gd['accused_student']['first_name']}, nice to meet you'''
        if THIS_SEMESTER == 'Spring':
            course['conversation_date'] = f'{THIS_YEAR}-01-15'
        else:
            course['conversation_date'] = f'{THIS_YEAR}-08-20'
        course['conversation_time'] = f'09:{(index+12)%60}'
        insert_conversation(cursor, course['conversation_date'],
                            course['conversation_time'], conversation,
                            [course['teacher_id'], gd['accused_student']['id']])

        # Insert the transcription of the accused conversation
        conversation = f'''I'm sorry {gd['accused_student']['first_name']}, but the
video clearly shows a {'man' if gd['accused_student']['gender'] else 'woman'} with
{gd['accused_student']['hair_color']} hair and {gd['accused_student']['eye_color']} eyes
talking to another student during the exam.'''
        if THIS_SEMESTER == 'Spring':
            course['conversation_date'] = f'{THIS_YEAR}-01-31'
        else:
            course['conversation_date'] = f'{THIS_YEAR}-09-05'
        course['conversation_time'] = f'09:{(index+12)%60}'
        insert_conversation(cursor, course['conversation_date'],
                            course['conversation_time'], conversation,
                            [course['teacher_id'], gd['accused_student']['id']])

        conn.commit()
        return course

def insert_conversation(cursor, what_date, what_time, conversation, ids):
    ''' Insert a conversation on the date and time with the list of ids '''
    cursor.execute("""INSERT INTO Transcription (what_date, what_time, conversation)
                                         VALUES (:what_date, :what_time, :conversation)
                   RETURNING transcription_id""",
                   dict(what_date=what_date,
                        what_time=what_time,
                        conversation=conversation))
    transcription_id = cursor.lastrowid

    for s_id in ids:
        cursor.execute("""INSERT INTO Conversation_participants (transcription_id, id)
                                                       VALUES (:transcription_id, :id)""",
                       dict(transcription_id=transcription_id,
                            id=s_id))

    return transcription_id


crime_type_index = 0
index = 0
gameData = dict(NUM_TEAMS=NUM_TEAMS, NUM_MEMBERS=NUM_MEMBERS)  # dict indexed by f'{team_number}{member_number}'
for team in range(NUM_TEAMS+1):
    for member in range(NUM_MEMBERS):
        game_index = f'game{team}{member}'
        gameData[game_index] = dict(database=f'game-university.{game_index}.sqlite')

        # Make the sqlite database file
        if os.path.isfile(gameData[game_index]['database']):
            os.remove(gameData[game_index]['database'])
        conn = sqlite3.connect(gameData[game_index]['database'])
        conn.row_factory = sqlite3.Row
        create_tables(conn)
        populate_tables(conn, index)
        gameData[game_index]['student_advocate'] = get_student_advocate(conn, index)
        gameData[game_index]['accused_student'] = get_accused_student(conn, index, gameData[game_index])
        gameData[game_index]['course'] = get_course_with_accused_advocate(conn, gameData[game_index])

        gameData[game_index]['starting_description'] = 'John, need a description'
        gameData[game_index]['starting_description_query'] = 'SELECT * From ID_card'

        index += 1

# Get the schema
conn = sqlite3.connect(gameData[game_index]['database'])
conn.row_factory = sqlite3.Row
with closing(getCursor(conn)) as cursor:
    cursor.execute('''SELECT sql
                        FROM sqlite_schema
                       WHERE type='table'  ''')
    gameData['schema'] = re.sub("\n  *",
                                "\n     ",
                                "\n".join([x[0] for x in cursor.fetchall()]))

with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as fid:
    json.dump(gameData, fid)
