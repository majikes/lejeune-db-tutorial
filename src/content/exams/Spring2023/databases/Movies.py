#!/usr/bin/env python3
''' Create the movies.sqlite '''
# pylint: disable=invalid-name

import csv
import json
import re
import sqlite3
import os

in_grader = 'setup' in os.getcwd()  # If in setup working directory, your in the grader

db_fnames = ['ex_movies-1.sqlite', 'ex_movies-2.sqlite']
ratings_fname = 'title.ratings.tsv'
names_fname = 'name.basics.tsv'
titles_fname = 'title.basics.tsv'
principals_fname = 'title.principals.tsv'

marvel_tids = ['tt0109770', 'tt0120667', 'tt1502712',
               'tt5095030', 'tt0478970', 'tt1211837', 'tt9419884',
               'tt0145487', 'tt0316654', 'tt0413300', 'tt10443172', 'tt11579056', 'tt12291314',
               'tt13154232', 'tt1872181', 'tt2250912', 'tt4633694', 'tt6320628', 'tt9362722',
               'tt3480822',
               'tt13836554', 'tt13925114', 'tt2395427', 'tt4154756', 'tt4154796', 'tt6172666',
               'tt8875872', 'tt9303032',
               'tt6611130',
               'tt2015381', 'tt3896198', 'tt6791350',
               'tt0103923', 'tt0458339', 'tt12453644', 'tt14513804', 'tt1843866', 'tt3498820',
               'tt0371746', 'tt0772174', 'tt1228705', 'tt12453644', 'tt1300854',
               'tt0800080',  'tt11023848']
marvel_tids = sorted(set(marvel_tids))



def removePrefix(text, ch):
    """ given a text like t_id="tt00800080" and "t" char
        return the integer 800080"""
    t = re.sub(f'^{ch}+', '', text)
    return int(t)

conns = []
cursors = []
for db_fname in db_fnames:

    # Create the database anew
    if os.path.isfile(db_fname):
        os.remove(db_fname)
    conn = sqlite3.connect(db_fname)
    conns.append(conn)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = ON')
    cursors.append(cursor)

for cursor in cursors:
    cursor.execute("""
    	  CREATE TABLE Titles (
                  t_id INTEGER PRIMARY KEY,
                  primaryTitle text
              )
              """)

    cursor.execute("""
	  CREATE TABLE Ratings (
              r_id INTEGER PRIMARY KEY,
              t_id INTEGER,
              averageRating FLOAT,
              numVotes INTEGER,
              FOREIGN KEY(t_id) REFERENCES Titles(t_id)
          )
	  """)

    cursor.execute("""
	  CREATE TABLE Names (
              n_id INTEGER PRIMARY KEY,
              primaryName TEXT,
              birthYear INTEGER,
              deathYear INTEGER
          )
	  """)

    cursor.execute("""
	  CREATE TABLE WorkedOn (
              t_id INTEGER,
              n_id INTEGER,
              category TEXT,
              FOREIGN KEY(t_id) REFERENCES Titles(t_id),
              FOREIGN KEY(n_id) REFERENCES Names(n_id)
          )
	  """)
    cursor.connection.commit()

# Titles
with open(titles_fname, encoding="utf-8") as fd:
    rd = csv.reader(fd, delimiter="\t")
    next(rd)  # Ignore header
    titles = {}
    for row in rd:
        if row[0] in marvel_tids:
            titles[row[0]] = dict(primaryTitle=row[3])
            t_id = removePrefix(row[0], 't')
            for cursor in cursors:
                cursor.execute("""
                          INSERT INTO Titles (t_id, primaryTitle)
                                      VALUES (:tid, :title)  """,
                          dict(tid=t_id, title=row[3]))
assert len(titles) == len(marvel_tids)
for conn in conns:
    conn.commit()

# Ratings
with open(ratings_fname, encoding="utf-8") as fd:
    rd = csv.reader(fd, delimiter="\t")
    next(rd)  # Ignore header
    ratings = {}
    for row in rd:
        if row[0] in marvel_tids:
            ratings[row[0]] = dict(averageRating=row[1], numVotes=row[2])
            t_id = removePrefix(row[0], 't')
            for cursor in cursors:
                cursor.execute("""
                          INSERT INTO Ratings (t_id, averageRating, numVotes)
                               VALUES (:tid, :rating, :votes) """,
                               dict(tid=t_id, rating=row[1], votes=row[2]))
for conn in conns:
    conn.commit()

# Principals
with open(principals_fname, encoding="utf-8") as fd:
    rd = csv.reader(fd, delimiter="\t")
    next(rd)  # Ignore header
    principals = {}
    for row in rd:
        if row[0] in titles:
            if row[0] not in principals:
                principals[row[0]] = []
            if row[3] == 'actress':
                row[3] = 'actor'
            principals[row[0]].append(dict(n_id=row[2], category=row[3]))

# Names
n_ids = sorted(set([ x['n_id'] for k,v in principals.items() for x in v ]))
with open(names_fname, encoding="utf-8") as fd:
    rd = csv.reader(fd, delimiter="\t")
    next(rd)  # Ignore header
    names = []
    for row in rd:
        if row[0] in n_ids:
            n_id = removePrefix(row[0][1:], 'm')
            primaryName = row[1]
            birthYear = row[2]
            deathYear = row[3]
            if birthYear == '\\N':
                birthYear = None
            if deathYear == '\\N':
                deathYear = None
            for cursor in cursors:
                cursor.execute("""
                   INSERT INTO Names (n_id, primaryName, birthYear, deathYear)
                          VALUES (:nid, :name, :born, :died)
                          """,
                               dict(nid=n_id, name=primaryName, born=birthYear, died=deathYear))

for t_id, a in principals.items():
    t_id = removePrefix(t_id, 't')
    for d in a:
        n_id = d['n_id']
        category = d['category']
        n_id = removePrefix(n_id[1:], 'm')
        for cursor in cursors:
            cursor.execute("""
                  INSERT INTO WorkedOn (t_id, n_id, category)
                           VALUES (:tid, :nid, :category) """,
                                   dict(tid=t_id, nid=n_id, category=category))
for conn in conns:
    conn.commit()


cursor = conns[-1].cursor()
cursor.execute('PRAGMA foreign_keys = ON')
cursor.execute(""" INSERT INTO Names (n_id, primaryName, birthYear, deathYear)
                         VALUES (150, "John Majikes", 1800, Null)""")
cursor.execute(""" INSERT INTO WorkedOn (t_id, n_id, category)
                         VALUES (3480822, 150,  "writer")""")
# Question Titles starting with A, C, D
cursor.execute("""INSERT INTO Titles (primaryTitle) VALUES
               ('Ant-Woman COMP421'), ('Be Wary Of Left Joins'), ('Captain COMP421'), ('Doctor SQL'), ('Iron Database')
               RETURNING t_id""")
title_ids = cursor.fetchall()
# Question Names starting with Alex
cursor.execute("""INSERT INTO Names (primaryName, birthYear, deathYear) VALUES
                   ('Alex But Not Alexander', 2022, null),
                   ('Sam But Not Samuel', 2022, null),
                   ('Dave But Not Daven', 2022, null),
                   ('Chris But Not Christopher', 2022, null)
               RETURNING n_id""")
name_ids = cursor.fetchall()
# Question Age
cursor.execute("""INSERT INTO Ratings (t_id, averageRating, numVotes) VALUES
                   (:t_a, 1, 1),
                   (:t_b, 2, 2),
                   (:t_c, 3, 3),
                   (:t_d, 4, 4)
                   """,
               dict(t_a=title_ids[0][0],
                    t_b=title_ids[1][0],
                    t_c=title_ids[2][0],
                    t_d=title_ids[3][0]))
cursor.execute("""INSERT INTO WorkedOn (t_id, n_id, category) VALUES
                   (:t_a, :n_a, 'producer'),
                   (:t_b, :n_b, 'cinematographer'),
                   (:t_c, :n_c, 'composer'),
                   (:t_d, :n_d, 'editor')
                   """,
               dict(t_a=title_ids[0][0], n_a=name_ids[0][0],
                    t_b=title_ids[1][0], n_b=name_ids[1][0],
                    t_c=title_ids[2][0], n_c=name_ids[2][0],
                    t_d=title_ids[3][0], n_d=name_ids[3][0]))


conns[-1].commit()

# Get the schema
cursor.execute('''SELECT sql
                   FROM sqlite_schema
                  WHERE type='table'  ''')
schema = re.sub("\n  *",
                "\n     ",
                "\n".join([x[0] for x in cursor.fetchall()]))

with open('ex_movies.json', 'w', encoding='utf-8') as fid:
    json.dump(schema, fid)
