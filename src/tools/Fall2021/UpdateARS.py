#!/usr/bin/env python3

import contextlib
import db
import pandas


db.init() # Ensure tables set up
ARS_CSV = 'ARS.csv'

ars_table = pandas.read_csv(ARS_CSV)
ars_table.columns = ['onyen', 'pid', 'extended']

# Reset all extended to zero
connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   cursor.execute('''UPDATE roll
                     SET extended = 0
                     WHERE extended != 0'''
                 )
   connection.commit()

for index, row in ars_table.iterrows():
    connection = db.open_db()
    with contextlib.closing(connection):
       cursor = connection.cursor()
       cursor.execute('''SELECT exists (SELECT onyen 
                                        FROM roll
                                        WHERE onyen = %s)''',
                  [row.onyen],
                  )
       assert cursor.fetchone().exists, f"User {row.onyen} is not in table roll"

       cursor.execute('''UPDATE roll
                         SET extended = %(extended)s
                         WHERE onyen = %(onyen)s''',
                      {'onyen': row.onyen, 'extended': row.extended})
       print(f"Update user {row.onyen} to have extended time of {row.extended}")
       connection.commit()
