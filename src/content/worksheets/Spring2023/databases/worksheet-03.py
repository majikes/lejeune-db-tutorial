#!/usr/bin/env python3
import sqlite3
import os

fname = 'worksheet-03.sqlite'

if os.path.isfile(fname):
    os.remove(fname)

conn = sqlite3.connect(fname)
c = conn.cursor()
stmts = [ "DROP TABLE IF EXISTS Students",
          "CREATE TABLE Students (sid char(20), name char(20), login char(10), age integer, gpa real)",
          "INSERT INTO Students values ('53666', 'Jones', 'jones@cs', 18, 3.4)",
          "INSERT INTO Students values ('53688', 'Smith', 'smith@cs', 18, 3.2)",
          "INSERT INTO Students values ('53650', 'Smith', 'smith@math', 19, 3.9)",
         ]

for stmt in stmts:
   c.execute(stmt)
conn.commit()

