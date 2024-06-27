#!/usr/bin/env python3
""" Assign graduate students in class
 """

import contextlib
import db
from ZWSP import ZWSP

zwsp_object = ZWSP()

db.init() # Ensure tables set up

graduate_students = ['yfyang', 'xutian', 'akash23']

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   cursor.execute('''UPDATE ROLL set graduate_student=false''')

for gs in graduate_students:
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
           UPDATE Roll
              SET graduate_student=true
              WHERE onyen=%(onyen)s''',
                     dict(onyen=gs))
      connection.commit()

