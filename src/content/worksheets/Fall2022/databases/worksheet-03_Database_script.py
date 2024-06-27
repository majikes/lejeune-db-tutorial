#!/usr/bin/env python3
import sqlite3
import os

fname1 = 'students-A.sqlite'
fname2 = 'students-B.sqlite'

if os.path.isfile(fname1):
    os.remove(fname1)
if os.path.isfile(fname2):
    os.remove(fname2)

conn = sqlite3.connect(fname1)
c = conn.cursor()
stmts = [ "DROP TABLE IF EXISTS Students",
          "CREATE TABLE Students (sid char(20), name char(20), login char(10), age integer, gpa real)",
          "INSERT INTO Students values ('50000', 'Dave',  'dave@cs', 19, 3.3)",
          "INSERT INTO Students values ('53666', 'Jones', 'jones@cs', 18, 3.4)",
          "INSERT INTO Students values ('53688', 'Smith', 'smith@cs', 18, 3.2)",
          "INSERT INTO Students values ('53650', 'Smith', 'smith@math', 19, 3.9)",
          "INSERT INTO Students values ('53831', 'Madayan', 'madayan@music', 11, 1.8)",
          "INSERT INTO Students values ('53832', 'Guldu', 'guldu@music', 12, 2.0)",
          "DROP TABLE IF EXISTS Enrolled",
          "CREATE TABLE Enrolled (sid char(20), name char(20), grade char(2))",
          "INSERT INTO Enrolled values ('53688', 'Carnatic101', 'C')",
          "INSERT INTO Enrolled values ('53688', 'Reggae203', 'B')",
          "INSERT INTO Enrolled values ('53650', 'Topology112', 'A')",
          "INSERT INTO Enrolled values ('53666', 'History105', 'B')",
         ]

for stmt in stmts:
   c.execute(stmt)
conn.commit()

conn = sqlite3.connect(fname2)
c = conn.cursor()
stmts = [ "DROP TABLE IF EXISTS Students",
          "CREATE TABLE Students (sid char(20), name char(20), login char(10), age integer, gpa real)",
          "INSERT INTO Students values ('53666', 'Jones2', 'jones@cs', 18, 3.4)",
          "INSERT INTO Students values ('53688', 'Smith2', 'smith@cs', 18, 3.2)",
          "INSERT INTO Students values ('53650', 'Smith2', 'smith@math', 19, 3.9)",
          "INSERT INTO Students values ('53831', 'Madayan2', 'madayan@music', 11, 1.8)",
          "INSERT INTO Students values ('53832', 'Guldu2', 'guldu@music', 12, 2.0)",
          "DROP TABLE IF EXISTS Enrolled",
          "CREATE TABLE Enrolled (sid char(20), name char(20), grade char(2))",
          "INSERT INTO Enrolled values ('53688', 'Carnatic101', 'C')",
          "INSERT INTO Enrolled values ('53688', 'Reggae203', 'B')",
          "INSERT INTO Enrolled values ('53650', 'Topology112', 'A')",
          "INSERT INTO Enrolled values ('53666', 'History105', 'B')",
         ]
for stmt in stmts:
    c.execute(stmt)
conn.commit()
