#!/usr/bin/python3
''' Run the grader against all possible submissions
    Can't do homeworks here '''

# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation
from contextlib import closing
from datetime import datetime, timedelta
from subprocess import Popen

from COMP421.mypoll.src import db
from COMP421.mypoll.src.get_email import get_email
from COMP421.mypoll.src.tools.DemoWorksheetBonus import bonus_time as demo_bonus_time
from COMP421.mypoll.src.tools.WelcomeVideoWorksheetBonus import bonus_time as welcome_bonus_time
from COMP421.mypoll.src.tools.HomeworkA0Bonus import bonus_time as a0_bonus_time
from assessments import updateGrades, SUBMITTABLE_PAGES

db.init()

# Find all the assessments student could have ever submitted
conn = db.open_db()
with closing(conn.cursor()) as cursor:
    cursor.execute('''
       SELECT DISTINCT P.key, P.onyen
         FROM All_Submitted AS S, Post as P, Rubrics as R
        WHERE S.post_id=P.post_id AND
              S.key=R.key AND
              R.assessment_type != 'homework' AND
              S.post_id not in (SELECT post_id FROM Feedback)
        -- Ultimately grade.py ensures grading by post_id order      
        ORDER BY P.key, P.onyen  ''')
    key_onyen = cursor.fetchall()  # The keys/onyens to be graded/updated


for assessment in sorted({x.key for x in key_onyen}):
   print(f'Running grader for {assessment}')
   with open(f'./{assessment}.log', 'a', encoding='utf-8') as out,\
           Popen(['./grade.py', f'key={assessment}'], stdout=out) as process:
       process.wait()

# Are there any worksheet bonuses?
if datetime.now() < demo_bonus_time + timedelta(days=1):
    with open("./DemoWorksheetBonus.log", "w", encoding='utf-8') as out,\
            Popen(['./tools/DemoWorksheetBonus.py'], stdout=out) as process:
        process.wait()
if datetime.now() < welcome_bonus_time + timedelta(days=1):
    with open("./WelcomeVideoWorksheetBonus.log", "w", encoding='utf-8') as out,\
            Popen(['./tools/WelcomeVideoWorksheetBonus.py'], stdout=out) as process:
        process.wait()
if datetime.now() < a0_bonus_time + timedelta(days=1):
    with open("./HomeworkA0Bonus.log", "w", encoding='utf-8') as out,\
            Popen(['./tools/HomeworkA0Bonus.py'], stdout=out) as process:
        process.wait()

conn = db.open_db()
with closing(conn.cursor()) as cursor:
    for onyen in sorted({x.onyen for x in key_onyen}):
        print(f"Updating grades for {onyen}")
        updateGrades(cursor, onyen)
    conn.commit()

# Check for anything submitted by students that are not accessable
# Note that most things end at 8:00 AM.  So don't check at 8:00 AM
now = datetime.now().time()
if now.hour != 8 or now.minute != 0:
    conn = db.open_db()
    with closing(conn.cursor() ) as cursor:
        cursor.execute('''
           SELECT DISTINCT key
             FROM All_Submitted AS S, Roll AS R
            WHERE R.onyen=S.onyen AND
                  R.section='001'

           EXCEPT

           SELECT DISTINCT P.key
             FROM Pages P, Roll R
            WHERE (P.onyen=R.onyen or (P.onyen='' and P.section=R.section)) AND
                   R.section='001' AND
                   P.start_time <= now() AND
                   P.end_time >= now()
                  ''')
        for row in cursor.fetchall():
            print(f'Someone submitted "{row.key}" but cannot access it.')

# Check for any assessment submittable between LDOC and FE
conn = db.open_db()
with closing(conn.cursor() ) as cursor:
    cursor.execute("""
        SELECT Distinct P.key
           FROM Active_sections as A, Pages as P
           WHERE A.page_id = P.id AND
                 A.page_section in %(subsequent_submittable_pages)s AND
                 (P.start_time BETWEEN '2023-12-06 00:01:00' AND '2023-12-08 00:00:00' OR
                  P.end_time   BETWEEN '2023-12-06 00:01:00' AND '2023-12-08 00:00:00')  """,
                   dict(subsequent_submittable_pages=tuple(SUBMITTABLE_PAGES)))

    for row in cursor.fetchall():
        print(f'Assessment  "{row.key}" is submittable during finals week')

# Check for any tuples in roll table with null email
# This API only does about 10 REST calls before it stops working
conn = db.open_db()
with closing(conn.cursor()) as cursor:
    cursor.execute("""
        SELECT onyen 
          FROM roll
         WHERE section != '000' AND
               onyen not like 'student%' AND
               email is Null
         ORDER BY onyen   """)
    onyens = [x.onyen for x in cursor.fetchall()]
    for onyen in onyens[:10]:
        print(f'Update email address for onyen {onyen}')
        try:
            email = get_email(onyen)
            if email is None:
                email = 'unknown'
        except:
            print('Can not get email')
            raise
        cursor.execute("""
            UPDATE roll
               SET email = %(email)s
             WHERE onyen = %(onyen)s """,
                       dict(onyen=onyen,
                            email=email))
        conn.commit()
