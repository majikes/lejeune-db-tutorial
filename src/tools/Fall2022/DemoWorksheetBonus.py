#!/usr/bin/env python3
""" Give worksheet bonus to students who
    submit demo before 9:30 Tuesday 2022-01-11
 """
# pylint: disable=invalid-name

import contextlib
from datetime import datetime

from COMP421.mypoll.src import db
from COMP421.mypoll.src.assessments import updateGrades

bonus_date = datetime(2022, 8, 15, 9, 30)

db.init() # Ensure tables set up

reason = f'Submitted worksheet-00-demo before {bonus_date}'
connection = db.open_db()
demo_submitted = []
with contextlib.closing(connection):
    cursor = connection.cursor()
    cursor.execute('''
                 SELECT DISTINCT P.onyen
                   FROM Submitted S, Post P
                  WHERE S.key='worksheet-00-demo' AND
                        P.id=S.id AND
                        time < %(bonus_date)s AND
                        P.onyen not in (SELECT onyen
                                          FROM Worksheet_bonus
                                         WHERE reason = %(reason)s)
                  ''', dict(reason=reason, bonus_date=bonus_date))
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
