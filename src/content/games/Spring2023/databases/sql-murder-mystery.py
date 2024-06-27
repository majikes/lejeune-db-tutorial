#!/usr/bin/env python3
"""A script to load the sql-murder-mystery db from https://mystery.knightlab.com/ """
import sqlite3
from sqlite_dump import iterdump   # pip install sqlite-dump

input_fn = 'sql-murder-mystery.db'
output_fn = 'sql-murder-mystery-source'

conn = sqlite3.connect(input_fn)
with open(output_fn, 'w') as fid:
    for line in iterdump(conn):
        fid.write(line)
