#!/usr/bin/env python3
''' Use the created :qV file to assign Zoom breakout rooms '''

import contextlib
import db
import os.path as osp
import numpy as np
import pandas
import sys


db.init() # Ensure tables set up
TEAMS_CSV = { '001': osp.join('.', 'ZoomBreakout.001.csv'),
              '002': osp.join('.', 'ZoomBreakout.002.csv')}

for section in TEAMS_CSV: 
    rooms = pandas.read_csv(TEAMS_CSV[section])
    rooms.columns = ['room', 'email']

    # Check for errors
    teams = rooms.room.unique()
    assert len(teams) <= 50, f"{len(teams)} teams must be under 50"
    for team in teams:
       num_members = len(rooms[ rooms.room == team].email)
       assert num_members <= 5, f"Team {team} has {num_members} members, must be five or less"
       team_number = int(team[14:])  # Teams are 'Breakout Room \d\d'
       member_number = 0

       for email in rooms[ rooms.room == team].email:
          onyen = email.split('@')[0]
          member_number += 1

          connection = db.open_db()
          with contextlib.closing(connection):
             cursor = connection.cursor()
             cursor.execute('''SELECT T.member_number, T.team_number, R.section
                               FROM roll R
                               LEFT JOIN teams T
                                 ON R.onyen = T.onyen
                               WHERE R.onyen = %s 
                            ''',
                            [onyen],
                            )
             row = cursor.fetchone()
             assert row is not None, f"Onyen {onyen} is not in table roll"
             db_member_number = row.member_number
             db_team_number = row.team_number
             db_section = row.section
             assert row.section == section, f"Onyen {onyen} is in section {row.section} not {section}"

             if db_team_number != team_number:
                print(f"Moving onyen {onyen} from team {db_team_number} to {team_number}")
             if (db_team_number != team_number) or (db_member_number != member_number):
                cursor.execute('''
                    INSERT INTO teams
                        (onyen, member_number, team_number) 
                        VALUES (%(onyen)s, %(member_number)s, %(team_number)s)
                    ON CONFLICT (onyen) DO UPDATE SET
                        (onyen, member_number, team_number) =
                        (%(onyen)s, %(member_number)s, %(team_number)s)
                    ''',
                    {'onyen': onyen, 'member_number': member_number, 'team_number': team_number},
                )
                connection.commit()

