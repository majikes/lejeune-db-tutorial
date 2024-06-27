#!/usr/bin/env python
""" Create Football data """

# pylint: disable=line-too-long,invalid-name

import json
import os
import random
import re
import sqlite3
from collections import namedtuple
from contextlib import closing
from datetime import date, datetime

# https://blog.collegefootballdata.com/using-api-keys-with-the-cfbd-api/
import cfbd  # pip install cfbd
import dotenv

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

EXCLUDED_CONFERENCES = ['FBS Independents', 'American Athletic', 'Mid-American']
DB1_EXCLUDED_CONFERENCES = ['Conference USA', 'Mountain West', 'SEC', 'Sun Belt']
DATABASES = ['football-1.sqlite', 'football-2.sqlite']
YEAR = 2021 if datetime.today().date() < date(2022, 9, 1) else 2022 # Roster's aren't out yet

# Get all the data from cfbd
config = cfbd.Configuration()
config.api_key['Authorization'] = dotenv_values['CFBD_KEY']
config.api_key_prefix['Authorization'] = 'Bearer'

games_api = cfbd.GamesApi(cfbd.ApiClient(config))
games = games_api.get_games(year=YEAR)

confs_api = cfbd.ConferencesApi(cfbd.ApiClient(config))
confs = confs_api.get_conferences()
conferences = sorted({c.short_name for c in confs})

teams_api = cfbd.TeamsApi(cfbd.ApiClient(config))
fbs_teams = teams_api.get_fbs_teams(year=YEAR)
Fbs_Conf = namedtuple('Fbs_Conf', ('full_name', 'conf_id'))
fbs_confs = {}
for c in {t.conference for t in fbs_teams}:
    for c1 in confs:
        if c1.name == c:
            fbs_confs[c] = Fbs_Conf(full_name=c1.short_name,
                                              conf_id=0)


# Remove the old database
conns = []
for db in DATABASES:
    if os.path.exists(db):
        os.remove(db)
    conn = sqlite3.connect(db)
    conn.cursor().execute('PRAGMA foreign_keys = ON')
    conns.append(conn)

# Set up the Conferences, Stadiums, Teams, and Rosters relations
for index, conn in enumerate(conns):
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
                CREATE TABLE Conferences
                    (conf_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     long_name TEXT) ''')
        cursor.execute('''
                CREATE TABLE Conferences2
                    (conf_id INTEGER,
                     name TEXT,
                     long_name TEXT) ''')
        cursor.execute('''
                CREATE TABLE Teams
                    (team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     school_name TEXT,
                     mascot TEXT,
                     conf_id INTEGER,
                     FOREIGN KEY(conf_id) REFERENCES Conferences(conf_id) ON DELETE CASCADE) ''')
        cursor.execute('''
                CREATE TABLE Teams2
                    (team_id INTEGER,
                     school_name TEXT,
                     mascot TEXT,
                     conf_id INTEGER) ''')
        cursor.execute('''
                CREATE TABLE Stadiums
                    (stadium_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     capacity INTEGER,
                     city TEXT,
                     state TEXT,
                     zip TEXT,
                     latitude REAL,
                     longitude REAL,
                     elevation REAL,
                     team_id INTEGER,
                     FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE) ''')
        cursor.execute('''
                CREATE TABLE Stadiums2
                    (stadium_id INTEGER,
                     name TEXT,
                     capacity INTEGER,
                     city TEXT,
                     state TEXT,
                     zip TEXT,
                     latitude REAL,
                     longitude REAL,
                     elevation REAL,
                     team_id INTEGER) ''')
        cursor.execute('''
                CREATE TABLE Rosters
                    (roster_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     first_name TEXT,
                     last_name TEXT,
                     height INTEGER,
                     weight INTEGER,
                     year INTEGER,
                     position TEXT,
                     city TEXT,
                     state TEXT,
                     zip TEXT,
                     latitude REAL,
                     longitude REAL,
                     jersey_number INTEGER,
                     team_id INTEGER,
                     FOREIGN KEY(team_id) REFERENCES Teams(team_id) ON DELETE CASCADE )''')
        cursor.execute('''
                CREATE TABLE Rosters2
                    (roster_id INTEGER,  -- With nearly 12,000 players,
                     first_name TEXT,    -- a select of this entire relation 
                     last_name TEXT,     -- will take 10-15 seconds!
                     height INTEGER,
                     weight INTEGER,
                     year INTEGER,
                     position TEXT,
                     city TEXT,
                     state TEXT,
                     zip TEXT,
                     latitude REAL,
                     longitude REAL,
                     jersey_number INTEGER,
                     team_id INTEGER) ''')
        cursor.execute('''
            CREATE TABLE Games
                (game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 home_team_id INTEGER,
                 home_team TEXT,
                 away_team_id INTEGER,
                 away_team TEXT,
                 start_date TEXT,
                 stadium_id INTEGER,
                 completed INTEGER,               -- 0 False, otherwise True
                 conference_game INTEGER,         -- 0 False, otherwise True
                 attendance INTEGER DEFAULT NULL, -- NULL until game starts
                 home_points INTEGER,
                 away_points INTEGER,
                 week INTEGER,                    -- Conference week number
                 FOREIGN KEY(away_team_id) REFERENCES Teams(team_id) ON DELETE CASCADE,
                 FOREIGN KEY(home_team_id) REFERENCES Teams(team_id) ON DELETE CASCADE) ''')
        cursor.execute('''
            CREATE TABLE Games2
                (game_id INTEGER,
                 home_team_id INTEGER,
                 home_team TEXT,
                 away_team_id INTEGER,
                 away_team TEXT,
                 start_date TEXT,
                 stadium_id INTEGER,
                 completed INTEGER,               -- 0 False, otherwise True
                 conference_game INTEGER,         -- 0 False, otherwise True
                 attendance INTEGER DEFAULT NULL, -- NULL until game starts
                 home_points INTEGER,
                 away_points INTEGER,
                 week INTEGER)                    -- Conference week number ''')
        conn.commit()

        # Add all the conferences
        for c in sorted({t.conference for t in fbs_teams}, reverse=index==1):
            if c in EXCLUDED_CONFERENCES:
                continue
            cursor.execute('''
                    INSERT INTO Conferences
                                (name, long_name)
                         VALUES (:name, :long_name) ''',
                           dict(name=c, long_name=fbs_confs[c].full_name))
            conf_id = cursor.lastrowid
            fbs_confs[c] = Fbs_Conf(full_name=fbs_confs[c].full_name,
                                    conf_id=conf_id)
        conn.commit()

        # Add all the teams
        for t in sorted(fbs_teams, key=lambda x: x.mascot, reverse=index==1):
            if t.conference in EXCLUDED_CONFERENCES:
                continue
            cursor.execute('''
                    INSERT INTO Teams
                                (school_name, mascot, conf_id)
                         VALUES (:school_name, :mascot, :conf_id) ''',
                           dict(school_name=t.school, mascot=t.mascot,
                                conf_id=fbs_confs[t.conference].conf_id))
            if t.location['elevation'] is None:
                t.location['elevation'] = random.randint(100, 1000)
            if t.location['capacity'] is None or t.location['capacity'] == 0:
                t.location['capacity'] = random.randint(10000, 100000)
            team_id = cursor.lastrowid
            cursor.execute('''
                    INSERT INTO Stadiums
                                (name, capacity, city, state, zip, latitude, longitude, elevation, team_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                           (t.location['name'], t.location['capacity'], t.location['city'],
                            t.location['state'], t.location['zip'],
                            t.location['latitude'], t.location['longitude'],
                            t.location['elevation'], team_id))
            # Get the team's roster
            roster = teams_api.get_roster(year=YEAR, team=t.school)
            for r in sorted(roster, key=lambda x: x.last_name if x.last_name else '', reverse=index==1):
                if r.first_name is None and r.last_name is None:
                    continue
                cursor.execute('''
                    INSERT INTO Rosters
                                (first_name, last_name, height, weight, year, position, city,
                                state, zip, latitude, longitude, jersey_number, team_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                           (r.first_name, r.last_name, r.height, r.weight, r.year, r.position, r.home_city,
                            r.home_state, r.home_county_fips, r.home_latitude, r.home_longitude,
                            r.jersey, team_id))
        conn.commit()

        # Add the games
        for g in sorted(games, key=lambda x: (x.week, x.home_team), reverse=index==1):
            # Home team
            cursor.execute('''
                 SELECT T.team_id, S.stadium_id, S.name
                   FROM Teams AS T, Stadiums AS S
                  WHERE S.team_id=T.team_id AND
                        T.school_name=:school_name''',
                           dict(school_name=g.home_team))
            home = cursor.fetchone()
            if not home:
                home = (None, None, None)
            # Away team
            cursor.execute('''
                 SELECT T.team_id, S.stadium_id, S.name
                   FROM Teams AS T, Stadiums AS S
                  WHERE S.team_id=T.team_id AND
                        T.school_name=:school_name''',
                           dict(school_name=g.away_team))
            away = cursor.fetchone()
            if not away:
                away = (None, None, None)

            if home[0] or away[0]:
                # The game has at least one FBS team
                completed = datetime.now().strftime('%Y-%m-%d') > g.start_date[:10]
                conference_game = 1 if g.conference_game else 0
                cursor.execute('''
                    INSERT INTO Games
                                (home_team_id, home_team, away_team_id, away_team, start_date,
                                 stadium_id, completed, conference_game, attendance, home_points, away_points, week)
                         VALUES (:home_team_id, :home_team, :away_team_id, :away_team, :start_date,
                                 :stadium_id, :completed, :conference_game, :attendance, :home_points, :away_points, :week)''',
                               dict(home_team_id=home[0], home_team=g.home_team, away_team_id=away[0],
                                    away_team=g.away_team, start_date=g.start_date[:10],
                                    stadium_id=home[1], completed=completed, conference_game=conference_game,
                                    attendance=g.attendance, home_points=g.home_points, away_points=g.away_points, week=g.week))

        # Remove Games with NULL team_id's
        cursor.execute('''delete from games where away_team_id is null or home_team_id is null''')

        conn.commit()


# Change database 1 so that there are different answers for db1 versus db2
with closing(conns[1].cursor()) as cursor:
    # List.names
    # Add a conference
    conf_id = 99999
    cursor.execute('''
             INSERT INTO Conferences
                                (name, long_name)
                         VALUES ('Majikes', 'Raghuvara')''')
    # Add a team to teams
    conf_id = cursor.lastrowid
    cursor.execute('''
                    INSERT INTO Teams
                                (school_name, mascot, conf_id)
                         VALUES ('Chicago', 'Bad news bears', :conf_id)''',
                   dict(conf_id=conf_id))
    team_id = cursor.lastrowid
    # Add a stadium
    cursor.execute('''
                    INSERT INTO Stadiums
                                (name, capacity, city, state, zip, latitude, longitude, elevation, team_id)
                         VALUES ('Mason Park', 25, 'Chicago', 'IL', 11111, 1, 3, 5, :team_id) ''',
                           dict(team_id=team_id))
    # Don't need to add players as they're added later
    # Schools With Roster Size
    # Add me to Notre Dame so 99->100, Georgia State so 109->110, Virginia so 119->120, USC 128->130
    cursor.execute('''
         INSERT INTO Rosters (team_id, first_name, last_name, height, weight, year, position, city,
                              state, zip, latitude, longitude, jersey_number)
                      SELECT team_id team_id, 'John' first_name, 'Majikes' last_name,
                             74 height, 180 pounds, 4 year, 'CB' position,
                             'Apex' city, 'NC' state, '27502' zip, 0.0 latitude, 0.0 longitude, 72 jersey_number
                        FROM Teams       
                       WHERE school_name in ('Notre Dame', 'Penn State', 'North Carolina', 'Georgia State', 'Virginia', 'USC')''')
    cursor.execute('''
         INSERT INTO Rosters (team_id, first_name, last_name, height, weight, year, position, city,
                              state, zip, latitude, longitude, jersey_number)
                      SELECT team_id team_id, 'J' first_name, 'Majikes' last_name,
                             74 height, 180 pounds, 4 year, 'CB' position,
                             'Apex' city, 'NC' state, '27502' zip, 0.0 latitude, 0.0 longitude, 72 jersey_number
                        FROM Teams       
                       WHERE school_name in ('USC')''')

    # Relational_Algebra_Query
    # Move 'Jerry Richardson Stadium' from zip 28223 to 60001
    cursor.execute(''' UPDATE Stadiums
                          SET zip = 60001
                        WHERE name = 'Jerry Richardson Stadium'  ''')
    # Move 'Folsom Field' from zip 80309 to 60001
    cursor.execute(''' UPDATE Stadiums
                          SET zip = 60001
                        WHERE name = 'Folsom Field'  ''')

    # List.Stadiums
    # Don't have to do anything because Teams.In.Conferences added Kansas State to ACC so 'Bill Synder Family Football Stadium' in ACC

    # Teams.In.Conferences
    # Move Kansas State from Big 12 to Atlantic Coast Conference
    cursor.execute(''' UPDATE Teams
                          SET conf_id= (SELECT conf_id FROM Conferences WHERE long_name='Atlantic Coast Conference')
                        WHERE school_name = 'Kansas State'  ''')
    # Move Temple from the American Athletic Conference to the Pac-12 Conference
    cursor.execute(''' UPDATE Teams
                          SET conf_id= (SELECT conf_id FROM Conferences WHERE long_name='Pac-12 Conference')
                        WHERE school_name = 'Temple'  ''')

    # Home.Team
    # Give UMass's score to Pittsburgh in week 1
    cursor.execute(''' UPDATE Games SET home_points=7, away_points=51
                              WHERE home_team='Pittsburgh' AND
                                    away_team='UMass' AND
                                    week=1 ''')

    # List.Games
    # Add a ACC game at a higher/lowest elevation largest/smallest latitude than miami/virginia tech/syracuse
    cursor.execute('''
           UPDATE Stadiums
               SET elevation=632.2631226, latitude=43.0362269
            WHERE name = 'Bill Snyder Family Football Stadium' ''')
    cursor.execute('''
           UPDATE Stadiums
               SET elevation=2.624486446, latitude=25.9579665
            WHERE name = 'Kenan Memorial Stadium' ''')

    # Make sure no games have null points
    cursor.execute('''UPDATE Games SET home_points=0 WHERE home_points is NULL;''')
    cursor.execute('''UPDATE Games SET away_points=0 WHERE away_points is NULL;''')

    for c in DB1_EXCLUDED_CONFERENCES:
        cursor.execute('''DELETE FROM Conferences
                            WHERE name=:name ''',
                   dict(name=c))

    cursor.connection.commit()

for index, conn in enumerate(conns):
    with closing(conn.cursor()) as cursor:
        for t in ['Games', 'Rosters', 'Stadiums', 'Teams', 'Conferences']:
            print(f'Renaming conference {t}')
            cursor.execute(f'''INSERT INTO {t}2 SELECT * FROM {t}''')
            cursor.execute(f'''DROP TABLE {t}''')
            cursor.execute(f'''ALTER TABLE {t}2 RENAME TO {t} ''')
        cursor.connection.commit()

# Get the schema
with closing(conns[0].cursor()) as cursor:
    cursor.execute('''SELECT sql
                       FROM sqlite_schema
                      WHERE type='table'  ''')
    schema = re.sub("\n  *",
                    "\n     ",
                    "\n".join([x[0] for x in cursor.fetchall()]))
    schema = re.sub(r'CREATE TABLE sqlite_sequence\(name,seq\)\n', '', schema)
    schema = re.sub('"Conferences"', 'Conferences', schema)
    schema = re.sub('"Stadiums"', 'Stadiums', schema)
    schema = re.sub('"Teams"', 'Teams', schema)
    schema = re.sub('"Rosters"', 'Rosters', schema)
    schema = re.sub('"Games"', 'Games', schema)

    with open(DATABASES[0].replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
        json.dump(schema, fid)
