#!/usr/bin/env python3
""" Give worksheet bonus to students who
    watch welcome video before FDOC 8:00 AM
 """
# pylint: disable=invalid-name

import contextlib
from datetime import datetime

from COMP421.mypoll.src import db
from COMP421.mypoll.src.assessments import updateGrades
from COMP421.mypoll.src.config import first_day_of_classes, welcome_video_hexcode

bonus_time = datetime(first_day_of_classes.year, first_day_of_classes.month,
                      first_day_of_classes.day, 8, 0)

db.init() # Ensure tables set up

reason = f'Watched welcome video before {bonus_time}'
connection = db.open_db()
demo_submitted = []
with contextlib.closing(connection):
    cursor = connection.cursor()
    # Should not use f-string but wanted to generalize hexcode
    cursor.execute(f'''
                 SELECT DISTINCT F.onyen
                   FROM Fetched as F
                  WHERE F.url like  '%%panopto%%{welcome_video_hexcode}' AND
                        F.time < %(bonus_time)s AND
                        F.onyen not in (SELECT onyen
                                          FROM Worksheet_bonus
                                         WHERE reason = %(reason)s)
                  ''', dict(reason=reason, bonus_time=bonus_time))
    demo_submitted = [row.onyen for row in cursor.fetchall()]

for onyen in demo_submitted:
    print(f"Adding Welcome video bonus for {onyen}")
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
