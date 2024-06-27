#!/usr/bin/env python3
''' Analyze team worksheets to get the teams '''

import contextlib
import db
import os.path as osp
import numpy as np
import pandas
import sys
from collections import namedtuple


db.init() # Ensure tables set up

# select * from post where id=13;
# select * from answer where postid=13
# select distinct on (P.onyen)  P.id, P.onyen from post P, answer A where P.key='worksheet00-teams' and P.id = A.postid and A.field = '_submit' and A.value like '%%Submit%%' order by P.onyen, P.id;

KEY='worksheet-00-teams'

PROBABLY_DROPPED = ['mfaragg', 'dogado99', 'hptaylor', 'cassitea', 'lside']

connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   cursor.execute('''SELECT onyen
                       FROM Roll
                      WHERE section='001' AND
                            onyen not in ('student1', 'student2', 'student3', 'student4') AND
                            onyen NOT IN (SELECT onyen
                                            FROM Submitted
                                           WHERE key=%(key)s)  ''',
                  dict(key=KEY))
   unsubmitted = [row.onyen for row in cursor.fetchall()]

connection = db.open_db()
with contextlib.closing(connection):
    cursor = connection.cursor()
    cursor.execute('''
    WITH S1 AS (SELECT S.onyen, value as student1
                  FROM Answer A, Submitted S
                 WHERE A.postid=S.id AND
                       field='Student.1' AND
                       S.key = %(key)s),
         S2 AS (SELECT S.onyen, value as student2
                  FROM Answer A, Submitted S
                 WHERE A.postid=S.id AND
                       field='Student.2' AND
                       S.key = %(key)s),
         S3 AS (SELECT S.onyen, value as student3
                  FROM Answer A, Submitted S
                 WHERE A.postid=S.id AND
                       field='Student.3' AND
                       S.key = %(key)s)
 
   SELECT R.onyen, S1.student1, S2.student2, S3.student3
     FROM Roll as R, S1, S2, S3
    WHERE R.onyen not in ('student1', 'student2', 'student3', 'student4') AND
          R.section = '001' AND
          R.onyen=S1.onyen AND
          R.onyen=S2.onyen AND
          R.onyen=S3.onyen
    ORDER BY R.onyen, S1.student1, S2.student2, S3.student3 ''',
                   dict(key=KEY))
    rows = []
    for row in cursor.fetchall():
        team = [row.onyen, row.student1, row.student2, row.student3]
        if team[1] == 'NONE':
            team[1]=''
        if team[2] == 'NONE':
            team[2]=''
        if team[3] == 'NONE':
            team[3]=''
        team = sorted(team)
        while team[0] == '':
            team = team[1:]
        rows.append(sorted(team))
rows_copy = rows
team_selection = sorted(rows)
teams_sizes = {'1': [], '2': [], '3': [], '4': []}
def exists(x, verbose=True):
    for i in teams_sizes:
        for j in teams_sizes[i]:
            for k in j:
                if k == x:
                    if verbose:
                       print(f'Found {x} in teams_sizes[{i}] with value {j}')
                    return True
    return False

# Manual team selection
teams_sizes['2'].append(['ira01', 'zizhou'])
teams_sizes['2'].append(['lucymac', 'mayteeak'])
teams_sizes['4'].append(['lukeduck', 'paeron', 'shaurikd', 'tjkapur'])
teams_sizes['4'].append(['harinkim', 'ryantj', 'sep0225', 'vlalitha'])
teams_sizes['3'].append(['haydend', 'jnchay', 'ypeter'])
teams_sizes['2'].append(['jessikka', 'wlan'])
teams_sizes['1'].append(['sjt49'])
while len(team_selection) > 0:
    c = team_selection.count(team_selection[0])
    if len(team_selection[0]) != c:
        already_exists = False
        for i in team_selection[0]:
            if exists(i, verbose=False):
                already_exists = True
        if already_exists:
           print(f'For team selection {team_selection[0]}, there are not {c} copies of it.')
        team_selection = team_selection[1:]
    elif c == 1:
        teams_sizes['1'].append(team_selection[0])
        team_selection = team_selection[1:]
    elif c == 2:
        teams_sizes['2'].append(team_selection[0])
        team_selection = team_selection[2:]
    elif c == 3:
        teams_sizes['3'].append(team_selection[0])
        team_selection = team_selection[3:]
    elif c == 4:
        teams_sizes['4'].append(team_selection[0])
        team_selection = team_selection[4:]
    else:
        import pdb; pdb.set_trace()

connection = db.open_db()
with contextlib.closing(connection):
    cursor = connection.cursor()
    cursor.execute('''SELECT onyen
                        FROM Roll
                       WHERE section='001' AND
                             onyen not like 'student%' ''')
    onyens = [row.onyen for row in cursor.fetchall()]
    for t in teams_sizes.values():
        for a in t:
            for o in a:
                if o not in onyens:
                    print(f'Onyen {o} is in teams_sizes but not in section 1')

    for onyen in onyens:
        if not exists(onyen, verbose=False):
            teams_sizes['1'].append([onyen])

for k in teams_sizes:
    print(f'There are {len(teams_sizes[k])} in teams_sizes[{k}]')

teams = [x for x in range(39)]
# Row A 8, 4, 17, 68
teams[0]  = teams_sizes['4'][0]
teams[1]  = teams_sizes['4'][1]
teams[2]  = teams_sizes['4'][2]
teams[3]  = teams_sizes['3'][0]
# Row B 5, 3, 17, 68
teams[4]  = teams_sizes['4'][3]
teams[5]  = teams_sizes['4'][4]
teams[6]  = teams_sizes['4'][5]
teams[7]  = teams_sizes['4'][6]
# Row C 1, 3, 17, 68
teams[8]  = teams_sizes['4'][7]
teams[9]  = teams_sizes['2'][0] + teams_sizes['2'][1]
teams[10] = teams_sizes['2'][2] + teams_sizes['2'][3]
teams[11] = teams_sizes['2'][4] + teams_sizes['2'][5]
# Row D 0, 3, 11, 68
teams[12] = teams_sizes['2'][6] + teams_sizes['2'][7]
teams[13] = teams_sizes['3'][1]
teams[14] = teams_sizes['2'][8] + teams_sizes['2'][9]
teams[15] = teams_sizes['3'][2]
# Row E 0, 1, 7, 68
teams[16] = teams_sizes['3'][3] + teams_sizes['1'][0]
teams[17] = teams_sizes['2'][10] + teams_sizes['2'][11]
teams[18] = teams_sizes['2'][12] + teams_sizes['2'][13]
teams[19] = teams_sizes['2'][14] + teams_sizes['2'][15]
# Row F 0, 0, 1, 67
teams[20] = teams_sizes['2'][16] + teams_sizes['1'][1] + teams_sizes['1'][2]
teams[21] = [teams_sizes['1'][x][0] for x in range(3,7)]
teams[22] = [teams_sizes['1'][x][0] for x in range(7,11)]
teams[23] = [teams_sizes['1'][x][0] for x in range(11,15)]
# Row G 0, 0, 0, 53
teams[24] = [teams_sizes['1'][x][0] for x in range(15,19)]
teams[25] = [teams_sizes['1'][x][0] for x in range(19,23)]
teams[26] = [teams_sizes['1'][x][0] for x in range(23,27)]
teams[27] = [teams_sizes['1'][x][0] for x in range(27,30)]
# Row H 0, 0, 0, 38
teams[28] = [teams_sizes['1'][x][0] for x in range(30,34)]
teams[29] = [teams_sizes['1'][x][0] for x in range(34,37)]
teams[30] = [teams_sizes['1'][x][0] for x in range(37,41)]
teams[31] = [teams_sizes['1'][x][0] for x in range(41,44)]
# Row I 0, 0, 0, 24
teams[32] = [teams_sizes['1'][x][0] for x in range(44,48)]
teams[33] = [teams_sizes['1'][x][0] for x in range(48,51)]
teams[34] = [teams_sizes['1'][x][0] for x in range(51,55)]
teams[35] = [teams_sizes['1'][x][0] for x in range(55,58)]
# Row J 0, 0, 0, 10
teams[36] = [teams_sizes['1'][x][0] for x in range(58,61)]
teams[37] = [teams_sizes['1'][x][0] for x in range(61,63)]
teams[38] = [teams_sizes['1'][x][0] for x in range(63,67)]


# Chapman 201 Left handed seats A4, B6, C-J7, A9, B12, C14, D15, E16, F17, G18, H19, J10
seats = [f'A-{i}' for i in range(1,16)] + \
        [f'B-{i}' for i in range(1,17)] + \
        [f'C-{i}' for i in range(1,17)] + \
        [f'D-{i}' for i in range(1,15)] + \
        [f'E-{i}' for i in range(1,17)] + \
        [f'F-{i}' for i in range(1,17)] + \
        [f'G-{i}' for i in range(1,16)] + \
        [f'H-{i}' for i in range(1,15)] + \
        [f'I-{i}' for i in range(1,15)] + \
        [f'J-{i}' for i in range(1,10)]

team_index = 0
seat_index = 0
onyens_used = set()
connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   cursor.execute('''UPDATE Teams
                        SET member_number=0, team_number=0
                      WHERE onyen IN (SELECT onyen
                                        FROM Roll
                                       WHERE section='001' and
                                             onyen not like 'student%')''') 
   while team_index < len(teams):
       for m in range(len(teams[team_index])):
           try:
             if teams[team_index][m] in onyens_used:
               import pdb; pdb.set_trace()
           except: 
               import pdb; pdb.set_trace()
           onyens_used.add(teams[team_index][m])
           print(f'Onyen {teams[team_index][m]} is on team {team_index} and sits in seat {seats[seat_index]}')
           cursor.execute('''UPDATE Teams
                                SET member_number=%(member)s, team_number=%(team)s
                              WHERE onyen=%(onyen)s''',
                          dict(onyen=teams[team_index][m], team=team_index+1, member=m))
           cursor.execute('''UPDATE Roll
                                SET exam_seat=%(seat)s
                               WHERE onyen=%(onyen)s''',
                          dict(onyen=teams[team_index][m], seat=seats[seat_index]))
           seat_index += 1
       team_index += 1
   connection.commit()

import sys
sys.exit()
import pdb; pdb.set_trace()
connection = db.open_db()
with contextlib.closing(connection):
   cursor = connection.cursor()
   cursor.execute('''select distinct on (P.onyen) P.id, P.onyen
                     from post P, answer A 
                     where P.key= %(key)s 
                       and P.id = A.postid 
                       and A.field = '_submit' 
                       and A.value like '%%Submit%%'
                     order by P.onyen, P.id''',
                     {'key': KEY},
                  )
   rows = [{'postid': row.id, 'onyen': row.onyen}
           for row in cursor.fetchall() ]

team_choices = []
for row in rows:
   connection = db.open_db()
   with contextlib.closing(connection):
      cursor = connection.cursor()
      cursor.execute('''select value 
                        from answer 
                        where postid = %(postid)s
                          and field in ('Student.1', 'Student.2', 'Student.3') ''',
                     {'postid': row['postid']},
                     )
      choices = [ x.value for x in cursor.fetchall() ]
      choices.append(row['onyen'])
      while 'NONE' in choices:
         index = choices.index('NONE')
         choices.pop(index)
      while '' in choices:
         index = choices.index('')
         choices.pop(index)

      choices = sorted(choices, reverse=True)
      team_choices.append(choices)
team_choices.sort(key=lambda x: str(x))

 
final_teams = {} 
team_sections = {}
for team in team_choices:
   team = tuple(team)
   if 'jmajikes' in team:
       continue
   if team not in final_teams.keys():
       connection = db.open_db()
       with contextlib.closing(connection):
           cursor = connection.cursor()
           cursor.execute('''select distinct(section)
                             from roll
                             where onyen in %s
                          ''',
                          [ team ],
                          )
           sections = cursor.fetchall()
           if len(sections) != 1:
              print(f"For team {team} members are in sections {sections}")
       final_teams[team] = 0
       team_sections[team] = sections[0].section
   final_teams[team] += 1

final_teams2 = {1: [], 2: [], 3:[], 4: []} 
for team in final_teams:
   if len(team) == final_teams[team]:
      final_teams2[len(team)].append(team)
   else:
      print(f"Mismatch {len(team)} {team}")

for section in ['002', '001']:
   print("Section ", section)
   for index in range(4,0, -1):
     for team in final_teams2[index]:
        if section ==team_sections[team]:
             print(team)
  
import pdb; pdb.set_trace()
