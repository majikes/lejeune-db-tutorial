#!/usr/bin/env python3
""" Give worksheet bonus to students who
    submit demo before FDOC 8:00 AM
 """
# pylint: disable=invalid-name

import contextlib
from datetime import datetime

from COMP421.mypoll.src import db
from COMP421.mypoll.src.assessments import updateGrades
from COMP421.mypoll.src.config import first_day_of_classes

bonus_time = datetime(first_day_of_classes.year, first_day_of_classes.month,
                      first_day_of_classes.day, 8, 0)

db.init() # Ensure tables set up

reason = f'Submitted worksheet-00-demo before {bonus_time}'
connection = db.open_db()
demo_submitted = []
with contextlib.closing(connection):
    cursor = connection.cursor()
    cursor.execute('''
                 SELECT DISTINCT P.onyen
                   FROM All_Submitted S, Post P
                  WHERE S.key='worksheet-00-demo' AND
                        P.post_id=S.post_id AND
                        time < %(bonus_time)s AND
                        P.onyen not in (SELECT onyen
                                          FROM Worksheet_bonus
                                         WHERE reason = %(reason)s)
                  ''', dict(reason=reason, bonus_time=bonus_time))
    demo_submitted = [row.onyen for row in cursor.fetchall()]

for onyen in demo_submitted:
    print(f"Adding Demo worksheet bonus for {onyen}")
    connection = db.open_db()
    with contextlib.closing(connection):
        cursor = connection.cursor()
        cursor.execute('''
                    INSERT INTO Worksheet_bonus
                      (onyen, submitter, reason)
                      VALUES( %(onyen)s, 'jmajikes', %(reason)s )''',
                     dict(onyen=onyen, reason=reason))
        updateGrades(cursor, onyen)
        connection.commit()
