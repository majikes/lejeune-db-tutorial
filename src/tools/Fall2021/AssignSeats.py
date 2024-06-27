#!/usr/bin/env python3
""" Arbitrary assign each student to a team
    For now, this is required for some things
    In the future, we really should not require teams
 """

import contextlib
from copy import copy
import db
from ZWSP import ZWSP

back_of_class = ['rebeccca']

zwsp_object = ZWSP()

db.init() # Ensure tables set up


every_other_seats = [f'A-{i}' for i in range(1, 12, 2)] + \
                    [f'B-{i}' for i in range(1, 13, 2)] + \
                    [f'C-{i}' for i in range(1, 14, 2)] + \
                    [f'D-{i}' for i in range(1, 15, 2)] + \
                    [f'E-{i}' for i in range(2, 15, 2)] + \
                    [f'F-{i}' for i in range(1, 15, 2)] + \
                    [f'G-{i}' for i in range(1, 15, 2)] + \
                    [f'H-{i}' for i in range(2, 15, 2)] + \
                    [f'I-{i}' for i in range(1, 15, 2)] + \
                    [f'J-{i}' for i in range(1,  9, 2)]
every_seats = [f'A-{i}' for i in range(1, 12)] + \
              [f'B-{i}' for i in range(1, 13)] + \
              [f'C-{i}' for i in range(1, 14)] + \
              [f'D-{i}' for i in range(1, 15)] + \
              [f'E-{i}' for i in range(1, 15)] + \
              [f'F-{i}' for i in range(1, 15)] + \
              [f'G-{i}' for i in range(1, 15)] + \
              [f'H-{i}' for i in range(1, 15)] + \
              [f'I-{i}' for i in range(1, 15)] + \
              [f'J-{i}' for i in range(1,  9)]
for broken in ['B-12', 'E-1', 'E-10', 'H-5', 'I-2']:
    if broken in every_other_seats:
        del every_other_seats[every_other_seats.index(broken)]
    if broken in every_seats:
        del every_seats[every_seats.index(broken)]

# ARS Seat assignments
if False:
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

for section in ['002', '001']:
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
                    SELECT R.onyen
                        FROM roll R, teams T
                        where section = %(section)s AND
                              -- extended = 0 AND
                              T.onyen = R.onyen
                        ORDER BY member_number desc, team_number
                      ''',
                     {'section': section},
                     )
      onyens = [row.onyen for row in cursor.fetchall()]
   if len(onyens) <= len(every_other_seats):
      seats = copy(every_other_seats)
   else:
      seats = copy(every_seats)
   assert len(onyens) <= len(seats)

   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      for index in range(len(onyens)):
         cursor.execute('''UPDATE Roll
                            SET exam_seat = %(seat)s
                            WHERE onyen=%(onyen)s''',
                        dict(onyen=onyens[index], seat=seats[index]))
      connection.commit()

for index in range(len(back_of_class)):
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
                    SELECT exam_seat 
                        FROM roll R
                        where exam_seat = %(seat)s
                      ''',
                     dict(seat=seats[-(index+1)])
                     )
      assert cursor.fetchone() is None, f' Cannot reassign {back_of_class[index]} because seat {seats[-(index+1)]} already used'

   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''UPDATE Roll
                         SET exam_seat = %(seat)s
                         WHERE onyen=%(onyen)s''',
                     dict(onyen=back_of_class[index], seat=seats[-(index+1)]))
      connection.commit()
