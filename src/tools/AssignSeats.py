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
exceptions = [['ctine987', 'A-5'],
              ['shriyam', 'A-1']]
exceptions = [['alan9213', 'O-18'],
              ['kevin975', 'O-16'],
              ['ojhern24', 'O-14'],
              ['pmathur', 'O-12'],
              ['eparke', 'O-10'],
              ['luiss', 'O-8'], 
              ['gwilson1', 'O-6'],
             ]

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

# Murphey 116 10 rows
# A1-A3 A5 broken, A6-A14, A16-A18
# B1-B3, B4-B15, B16-B18 same thru J, no row I
# K1, K5-K13, K18
seats = [f'A-{i}' for i in range(1,4)] + [f'A-{i}' for i in range(6,15)] + [f'A-{i}' for i in range(16, 19)]
seats =                                  [f'A-{i}' for i in range(6,15)]                                     + \
        [f'B-{i}' for i in range(1,4)] + [f'B-{i}' for i in range(4,16)] + [f'B-{i}' for i in range(16, 19)] + \
        [f'C-{i}' for i in range(1,4)] + [f'C-{i}' for i in range(4,16)] + [f'C-{i}' for i in range(16, 19)] + \
        [f'D-{i}' for i in range(1,4)] + [f'D-{i}' for i in range(4,16)] + [f'D-{i}' for i in range(16, 19)] + \
        [f'E-{i}' for i in range(1,4)] + [f'E-{i}' for i in range(4,16)] + [f'E-{i}' for i in range(16, 19)] + \
        [f'F-{i}' for i in range(1,4)] + [f'F-{i}' for i in range(4,16)] + [f'F-{i}' for i in range(16, 19)] + \
        [f'G-{i}' for i in range(1,4)] + [f'G-{i}' for i in range(4,16)] + [f'G-{i}' for i in range(16, 19)] + \
        [f'H-{i}' for i in range(1,4)] + [f'H-{i}' for i in range(4,16)] + [f'H-{i}' for i in range(16, 19)] + \
        [f'J-{i}' for i in range(1,4)] + [f'J-{i}' for i in range(4,16)] + [f'J-{i}' for i in range(16, 19)] + \
        [f'K-1']                       + [f'K-{i}' for i in range(5,14)] + [f'K-18']
print(f'The number of seats is {len(seats)}')

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

if False:
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
                     FROM roll R, grades G
                     where G.onyen = R.onyen AND
                           extended = 0 and
                           conflict_exam = false AND
                           R.onyen not like 'student%' AND
                           section in ('001', '002')
                     ORDER BY G.total, R.team_member_number desc, R.team_number asc
                   ''')
   onyens = [row.onyen for row in cursor.fetchall()]
   assert len(onyens) <= len(seats), F"{len(onyens)} {len(seats)}"

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   for index in range(len(onyens)):
      cursor.execute('''UPDATE Roll
                         SET team_member_number = %(member_number)s, team_number = %(team_number)s, exam_seat = %(seat)s
                         WHERE onyen=%(onyen)s''',
                     dict(onyen=onyens[index],
                          seat=seats[index],
                          team_number=(index//3),
                          member_number=(index%3)))
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
