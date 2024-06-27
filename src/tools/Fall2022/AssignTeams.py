#!/usr/bin/env python3
""" Arbitrary assign each student to a team
    For now, this is required for some things
    In the future, we really should not require teams
 """
# pylint: disable=bad-indentation, invalid-name, line-too-long

from contextlib import closing

from COMP421.mypoll.src.db import init, open_db
from COMP421.mypoll.src.ZWSP import ZWSP

NUM_MEMBERS = 4
NAMES = '''Narendra Panthee Himanshu Upadhyaya Abhijeet Khwaunju
Rahul Bade Lalan Siwakoti Narahari Sinha Roshan Chapagain
Shahid Rajkarnikar Dhananjay Nayak Chintan Yadav Satindra Ranjan
Sachin Khetan Jagadish Oli Gyan Baniya Rajiv Shah Badal Mathema
Yuvaraj Banskota Anjani Tripathi Ujwal Gajurel Kamal Wosti
Chandeshwor Khwaunju Manoj Sharma Praveen Adhikary Atul Basukala
Rajyeshwar Bhagat Om Nagargoje Indrajeet Jamarkattel Balraj
Tamarkar Rashmi Bagale Surendra Sitoula Byas Deuja Kashyap Parajuli
Prithivi Sainju Indrajeet Dharel Nawal Maskey Dileep Ghimire
Abhiman Bastola Rijendra Mishra Kuber Yonjan Raju Gyanwali
Yadab Budathoki Basistha Baniya Hemachandra Upadhya Aalok Vaidya
Alok Kashyap Bishal Devaki Jiwan Tshering Kabi Bhattachan Sudeep
Rayamajhi Parakram Tamang Bijendra Khwaunju Himanshu Gauchan
Vyas Pyakuryal Amod Sadaula Rajeev Bahadur Shyam Baruwal
Prajit Acharya Rashmi Syangden Pratik Modi Susan Pangeni
Rajiv Raut Pramesh Gartaula Balkrishan Shakya Naveen Hyoju
Raj Palikhe Prawal Khatioda Rabin Singh Kripal Mahto Himanshu
Oli Anjay Shrestha Balgovind Dhungel Chintan Aryal Sundip Shreesh
Roshan Gaundel Brijesh Madhikarmi Shambhu Raval Saurabh Karkee
Satyendra Mandal Abhiman Kunwar Shakti Jhapali Babu Bade
Manish Ranjan Amber Upadhya Bhakti Gartaula Rajan Byanjankar
Pritam Gupta Manmohan Panta Ranjan Khadgi Khagendra Gyawali
Maheshwar Gubhaju Kishor Kunwar Ballabh Batsa Bhavaroopa'''.split()

zwsp_object = ZWSP()

init() # Ensure tables set up


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
for index, admin in enumerate(admins):
   connection = open_db()
   with closing(connection):
      cursor = connection.cursor()
      onyen = admin
      cursor.execute(''' DELETE FROM Teams WHERE onyen=%(onyen)s  ''',
                     dict(onyen=onyen))
      cursor.execute('''
           INSERT INTO teams
              (onyen, member_number, team_number, alias_name)
           VALUES( %(onyen)s, %(member_number)s, %(team_number)s, %(alias_name)s)
           ON CONFLICT (onyen) DO UPDATE SET
              (member_number, team_number, alias_name) =
                     (%(member_number)s, %(team_number)s, %(alias_name)s)''',
                     dict(onyen=onyen, member_number=member_number,
                          team_number=team_number, alias_name=f'admin-{index}'))
      member_number = (member_number + 1) % NUM_MEMBERS
      connection.commit()

# Find unused names
connection = open_db()
with closing(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT alias_name FROM Teams")
    used = set(row.alias_name for row in cursor.fetchall())
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
         cursor.execute('''SELECT onyen, member_number, team_number, alias_name
                            FROM teams
                            WHERE onyen=%(onyen)s ''',
                        dict(onyen=onyen))
         try:
            row = cursor.fetchone()
            alias_name = row.alias_name
            found = True
         except:  # pylint: disable=bare-except
            found = False   # row is none

         member_number += 1
         if member_number%4 == 0:
            team_number += 1
            member_number = 0

         if not found or row.member_number != member_number or row.team_number != team_number or not row.alias_name:
            if row is None or not row.alias_name:
               alias_name = NAMES[name_index]
               name_index += 1
            cursor.execute('''
                 INSERT INTO teams
                    (onyen, member_number, team_number, alias_name)
                 VALUES( %(onyen)s, %(member_number)s, %(team_number)s, %(alias_name)s)
                 ON CONFLICT (onyen) DO UPDATE SET
                    (member_number, team_number, alias_name) =
                    (%(member_number)s, %(team_number)s, %(alias_name)s) ''',
                           dict(onyen=onyen, member_number=member_number,
                                team_number=team_number, alias_name=alias_name))
            connection.commit()
         print(f' {onyen} team number {team_number} member number {member_number} alias {alias_name} {name_index}')
