#!/usr/bin/env python3

# pip install us
import us

import csv
import sqlite3
import os

in_grader = 'setup' in os.getcwd()  # If in setup working directory, your in the grader

fname = 'worksheet-03.sqlite'
if os.path.isfile(fname):
   os.remove(fname)

conn = sqlite3.connect(fname)
cursor = conn.cursor()

create_table = '''
   create table if not exists Students
         (sid text,
         name text,
         login text,
         age integer,
         gpa real)'''
cursor.execute(create_table)

rows = [('53666', 'Jones', 'jones@cs', 18, 3.4),
        ('53688', 'Smith', 'smith@cs', 18, 3.2),
        ('53650', 'Smith', 'smith@math', 19, 3.9)]
for row in rows:
    cursor.execute('''
       INSERT INTO Students (sid, name, login, age, gpa)
                   VALUES (?, ?, ?, ?, ?)''',
                   row)
conn.commit()
cursor.execute('''SELECT count(*) from Students''')
assert cursor.fetchone()[0] == 3
