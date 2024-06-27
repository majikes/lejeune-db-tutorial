#!/usr/bin/env python3
""" Global 1015
 """

import contextlib
from copy import copy
import db

db.init() # Ensure tables set up

exceptions = [ ['chardorn', 'ARS'],
               ['elk1181',  'ARS'],
               ['jacob28',  'COMP 421'],
             ]
exceptions = [['wigalex', 'L-22']]
exceptions = []

# Global Center seating
seats = [f'A-{i}' for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]] + \
        [f'B-{i}' for i in [1,2,4,5,7,8,10,11,13,14,16,18]] + \
        [f'C-{i}' for i in [1,2,4,5,7,8,10,11,13,14,16,18]] + \
        [f'D-{i}' for i in [1,2,4,5,7,8,10,11,13,14,16,18]] + \
        [f'{x}-{i}' for x in 'EFGHIJKL' for i in [1,2,4,5,7,8,10,11,13,15,16,18,19,21,22]]

# Chapman 201 Left handed seats A4, B6, C-J7, A9, B12, C14, D15, E16, F17, G18, H19, J10
seats = [f'A-{i}' for i in [1,2,3,     5,6,7,8,                       10,11,12,13]] + \
        [f'B-{i}' for i in [1,2,4,5,   7,8,10,11,                     13,14,16,18]] + \
        [f'C-{i}' for i in [1,2,4,5,6, 8,10,11,13,                    15,16,18,19,20,21]] + \
        [f'D-{i}' for i in [1,2,4,5,6, 8,10,11,13,14,                 16,17,18,19,20,21,22]] + \
        [f'E-{i}' for i in [1,2,4,5,6, 8,10,11,13,14,15,              17,18,19,20,21,22,23]] + \
        [f'F-{i}' for i in [1,2,4,5,6, 8,10,11,13,14,15,16,           18,19,20,21,22,23,24]] + \
        [f'G-{i}' for i in [1,2,4,5,6, 8,10,11,13,14,15,16,17,        19,20,21,22,23,24,25]] + \
        [f'H-{i}' for i in [1,2,4,5,6, 8,10,11,13,14,15,16,17,18,19,  21,22,23,24,25,26,27]] + \
        [f'J-{i}' for i in [1,2,4,5,   7,8,                           11,12,13]]

# Howell 115
seats = [f'A-{i}' for i in range(1,16)] + \
        [f'B-{i}' for i in range(1,17)] + \
        [f'C-{i}' for i in range(1,17)] + \
        [f'D-{i}' for i in range(1,15)] + \
        [f'E-{i}' for i in range(1,16)] + \
        [f'F-{i}' for i in range(1,17)] + \
        [f'G-{i}' for i in range(1,16)] + \
        [f'H-{i}' for i in range(1,15)] + \
        [f'I-{i}' for i in range(1,15)] + \
        [f'J-{i}' for i in range(1,10)]


if True:
   # ARS Seat assignments
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
                    UPDATE Roll
                       SET exam_seat = 'ARS'
                       where section in ('001', '002') AND
                              extended != 0'''
                     )
      connection.commit()

if True:
   # Conflict Exam
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
                    UPDATE Roll
                       SET exam_seat = 'Chapman Hall Room 201'
                     WHERE section in ('001', '002') AND
                           conflict_exam = true AND
                           extended = 0'''
                     )
      connection.commit()

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   # This assumes no one is taking exam at ARS at exactly same time!
   cursor.execute('''
                 SELECT R.onyen
                     FROM roll R, teams T, grades G
                     where T.onyen = R.onyen AND
                           T.onyen = G.onyen AND
                           extended = 0 and
                           conflict_exam = false AND
                           T.onyen not like 'student%' AND
                           section in ('001', '002')
                     ORDER BY G.total, member_number desc, team_number asc
                   ''')
   onyens = [row.onyen for row in cursor.fetchall()]
   assert len(onyens) <= len(seats), F"{len(onyens)} {len(seats)}"

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   for index in range(len(onyens)):
      cursor.execute('''UPDATE Roll
                         SET exam_seat = %(seat)s
                         WHERE onyen=%(onyen)s''',
                     dict(onyen=onyens[index], seat=seats[index]))
      cursor.execute('''UPDATE Teams
                         SET member_number = %(member_number)s
                         WHERE onyen=%(onyen)s''',
                     dict(onyen=onyens[index], member_number=(index%3)))
   connection.commit()

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor() 
   for onyen, exam_seat in exceptions:
      cursor.execute('''UPDATE Roll
                           SET exam_seat=%(exam_seat)s
                         WHERE onyen=%(onyen)s''',
                     dict(exam_seat=exam_seat, onyen=onyen))
   connection.commit()
