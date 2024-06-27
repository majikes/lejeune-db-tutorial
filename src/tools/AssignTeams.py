#!/usr/bin/env python3
""" Arbitrary assign each student to a team
    For now, this is required for some things
    In the future, we really should not require teams
 """
# pylint: disable=bad-indentation, invalid-name, line-too-long

from contextlib import closing
from faker import Faker

from COMP421.mypoll.src.db import init, open_db
from COMP421.mypoll.src.ZWSP import ZWSP

NUM_MEMBERS = 4

init() # Ensure tables set up

connection = open_db()
with closing(connection):
   cursor = connection.cursor()
   cursor.execute('''
                 SELECT count(*) 
                     FROM roll   ''')
   num_names = cursor.fetchone()[0]
faker = Faker()
NAMES = [f'{faker.unique.last_name()}, {faker.suffix_nonbinary()}' for _ in range(num_names)]
NAMES = list(set([x.replace(', Jr.', ', Esq.') for x in NAMES]))
assert len(NAMES) == num_names

zwsp_object = ZWSP()

connection = open_db()
with closing(connection):
   cursor = connection.cursor()
   cursor.execute('''
                 SELECT onyen
                     FROM roll
                     where section = '003' ''')
   admins = [row.onyen for row in cursor.fetchall()]
print(f"admins={admins}")

# Set admin teams
member_number = 0
team_number = 0
connection = open_db()

for index, admin in enumerate(admins):
   connection = open_db()
   with closing(connection):
      cursor = connection.cursor()
      onyen = admin
      cursor.execute('''
           UPDATE ROLL SET team_number=%(team_number)s,
                           team_member_number=%(member_number)s
                  WHERE onyen=%(onyen)s   ''',
                     dict(onyen=onyen, member_number=member_number,
                          team_number=team_number, alias_name=f'admin-{index}'))
      cursor.execute('''
           UPDATE ROLL SET game_alias_name=%(alias_name)s
                  WHERE onyen=%(onyen)s AND
                        game_alias_name is NULL''',
                     dict(onyen=onyen, member_number=member_number,
                          team_number=team_number, alias_name=f'admin-{index}'))
      member_number = (member_number + 1) % NUM_MEMBERS
      connection.commit()

# Find unused names
connection = open_db()
with closing(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT game_alias_name FROM Roll")
    used = set(row.game_alias_name for row in cursor.fetchall())
    NAMES = list(set(NAMES) - used)

team_number = 0
member_number = 0
for section in ['002', '001']:
   connection = open_db()
   with closing(connection):
      cursor = connection.cursor()
      cursor.execute('''
                    SELECT onyen
                        FROM roll
                        where section = %(section)s 
                        ORDER BY onyen
                      ''',
                     dict(section=section))
      onyens = [row.onyen for row in cursor.fetchall()]
   print(f"onyens={onyens}")

   num_teams = len(onyens) // 4 + 2
   member_number = 0

   name_index = 0
   for onyen in onyens:
      connection = open_db()
      with closing(connection):
         cursor = connection.cursor()
         cursor.execute('''SELECT onyen, team_member_number, team_number, game_alias_name
                            FROM Roll
                            WHERE onyen=%(onyen)s ''',
                        dict(onyen=onyen))
         try:
            row = cursor.fetchone()
            alias_name = row.game_alias_name
            found = True
         except:  # pylint: disable=bare-except
            found = False   # row is none

         member_number += 1
         if member_number%4 == 0:
            team_number += 1
            member_number = 0

         if not found or row.team_member_number != member_number or row.team_number != team_number or not row.game_alias_name:
            if row is None or not row.game_alias_name:
               alias_name = NAMES[name_index]
               name_index += 1
            cursor.execute('''
                 UPDATE ROLL SET team_number=%(team_number)s,
                                 game_alias_name=%(alias_name)s,
                                 team_member_number=%(member_number)s
                        WHERE onyen=%(onyen)s  ''',
                           dict(onyen=onyen, member_number=member_number,
                                team_number=team_number, alias_name=alias_name))
            connection.commit()
         print(f' {onyen} team number {team_number} member number {member_number} alias {alias_name} {name_index}')
