#!/usr/bin/env python3

import contextlib
import db
import os.path as osp
import numpy as np
import pandas
import sys
from config import ZWSP


db.init() # Ensure tables set up
ZOOM_CSV = 'zoom.csv'

zoom_table = pandas.read_csv(ZOOM_CSV, sep='\t')
zoom_table.columns = ['url', 'type', 'section']

inserted_into_db = False
for index, row in zoom_table.iterrows():
    connection = db.open_db()
    cursor = connection.cursor()
    if row.section == '\\N':
       row.section = None
    if row.section is None:
       cursor.execute('''SELECT url, type, section
                     FROM zoom
                     where type = %s and section is null''',
                  [row.type],
                  )
    else:
       cursor.execute('''SELECT url, type, section
                     FROM zoom
                     where type = %(type)s and section = %(section)s''',
                  {'type': row.type, 'section': row.section},
                  )
    db_row = cursor.fetchone()
    if db_row is None:
       print(f"Inserting {row.url} {row.type} {row.section}")
    elif (db_row.type != row.type) or (db_row.section != row.section) or (db_row.url != row.url):
       print(f"Updating {row.url} for {row.type} {row.section} from {row.url} {row.type} {row.section}")
    if ((db_row is None) or
        ((db_row.type != row.type) or (db_row.section != row.section) or (db_row.url != row.url))):
       inserted_into_db = True
       if row.section is None:
          cursor.execute('''
              INSERT INTO zoom
                  (url, type, section) 
                  VALUES (%(url)s, %(type)s, NULL)
              ON CONFLICT (url, type, section) DO UPDATE SET
                  (url, type, section) =
                  (%(url)s, %(type)s, NULL)
              ''',
              {'url': row.url, 'type': row.type},
          )
       else:
          cursor.execute('''
              INSERT INTO zoom
                  (url, type, section) 
                  VALUES (%(url)s, %(type)s, %(section)s)
              ON CONFLICT (url, type, section) DO UPDATE SET
                  (url, type, section) =
                  (%(url)s, %(type)s, %(section)s)
              ''',
              {'url': row.url, 'type': row.type, 'section': row.section},
          )
       connection.commit()

if not inserted_into_db:
   print("No zoom table entries updated")
