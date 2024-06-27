#!/usr/bin/python3

import db
from datetime import datetime
import assessments
db.init()
conn = db.open_db()
cursor = conn.cursor()

now = datetime.now()
print(f"Updating COMP 421 grades at {now.strftime('%a, %Y/%m/%d %H:%M')}")

cursor.execute("SELECT onyen from roll where section != '000' ")
rows = cursor.fetchall()

if False:
   from collections import namedtuple
   Row = namedtuple('Row', 'onyen')
   rows = [ Row(onyen='jmajikes') ]
   import pdb; pdb.set_trace()

for row in rows:
   conn = db.open_db()
   cursor = conn.cursor()
   assessments.updateGrades(cursor, row.onyen)
   conn.commit()

cursor.execute("""
SELECT *
 FROM (SELECT key, count(*) as c
         FROM All_Submitted S, Roll R
        WHERE R.onyen=S.onyen AND
              section='001'
        GROUP BY key) as T
WHERE c>1 order by key""")
submitted_assessments = cursor.fetchall()
submitted_keys = set([x.key for x in submitted_assessments])

# available_assessments = assessments.get_all_assessments(cursor, 'rslutz', '001')
# available_keys = set([x.key for x in available_assessments])
# not_available = sorted(submitted_keys - available_keys - set(['game-sailors-1', 'game-sailors-2', 'game-sailors-3', 'game-sailors-4']))
# for key in not_available:
#     print(f'Key {key} appears in the submitted list but is not available for grade')
