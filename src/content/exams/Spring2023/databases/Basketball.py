#!/usr/bin/env python
""" Create Basketball data i

 Data files in One Drive COMP 421/basketball.
 They are not stored in git

"""

# pylint: disable=line-too-long, invalid-name, forgotten-debug-statement, too-many-lines, redefined-outer-name, bare-except, too-many-branches

from contextlib import closing
from collections import namedtuple
import json
import os
import re
import sqlite3
import pdb
from bs4 import BeautifulSoup

import pandas as pd
import requests
import numpy as np

DATABASES = ['midterm1-basketball-1.sqlite', 'midterm1-basketball-2.sqlite']
URL_BASE = "https://www.espn.com"
MISSING_TEAMS = ['Queens University Royals', 'IUPUI Jaguars',
                 'Brown Bears', 'Cornell Big Red', 'Columbia Lions',
                 "St. Thomas - Minnesota Tommies",
                 "Bethune-Cookman Wildcats", 'Dartmouth Big Green',
                 "Texas A&M-Commerce Lions", 'Harvard Crimson',
                 'Pennsylvania Quakers', 'Princeton Tigers',
                 'Yale Bulldogs',
                 'Maryland-Eastern Shore Hawks', 'Drake Bulldogs',
                 'UNC Greensboro Spartans',
                 "Stonehill Skyhawks", "Lindenwood Lions",
                 "Southern Indiana Screaming Eagles",
                 'Evansville Purple Aces', 'UIC Flames',
                 'Milwaukee Panthers']
ESPN_REMAP = namedtuple('ESPN_REMAP', 'espn_name team_name, nickname')
REMAP_TEAMS = [ESPN_REMAP(espn_name='Albany Great Danes',
                          team_name='Albany',
                          nickname='Great Danes'),
               ESPN_REMAP(espn_name='Jacksonville State Gamecocks',
                          team_name='Jacksonville St.',
                          nickname='Gamecocks'),
               ESPN_REMAP(espn_name='Kennesaw State Owls',
                          team_name='Kennesaw St.',
                          nickname='Owls'),
               ESPN_REMAP(espn_name='Wichita State Shockers',
                          team_name='Wichita St.',
                          nickname='Shockers'),
               ESPN_REMAP(espn_name='Florida State Seminoles',
                          team_name='Florida St.',
                          nickname='Seminoles'),
               ESPN_REMAP(espn_name='NC State Wolfpack',
                          team_name='North Carolina St.',
                          nickname='Wolfpack'),
               ESPN_REMAP(espn_name='Iowa State Cyclones',
                          team_name='Iowa St.',
                          nickname='Cyclones'),
               ESPN_REMAP(espn_name='Kansas State Wildcats',
                          team_name='Kansas St.',
                          nickname='Wildcats'),
               ESPN_REMAP(espn_name='Oklahoma State Cowboys',
                          team_name='Oklahoma St.',
                          nickname='Cowboys'),
               ESPN_REMAP(espn_name='Idaho State Bengals',
                          team_name='Idaho St.',
                          nickname='Bengals'),
               ESPN_REMAP(espn_name='Montana State Bobcats',
                          team_name='Montana St.',
                          nickname='Bobcats'),
               ESPN_REMAP(espn_name='Sacramento State Hornets',
                          team_name='Sacramento St.',
                          nickname='Hornets'),
               ESPN_REMAP(espn_name='Michigan State Spartans',
                          team_name='Michigan St.',
                          nickname='Spartans'),
               ESPN_REMAP(espn_name='Ohio State Buckeyes',
                          team_name='Ohio St.',
                          nickname='Buckeyes'),
               ESPN_REMAP(espn_name='Cal State Bakersfield Roadrunners',
                          team_name='Cal St. Bakersfield',
                          nickname='Roadrunners'),
               ESPN_REMAP(espn_name='Cal State Fullerton Titans',
                          team_name='Cal St. Fullerton',
                          nickname='Titans'),
               ESPN_REMAP(espn_name='Cal State Northridge Matadors',
                          team_name='Cal St. Northridge',
                          nickname='Matadors'),
               ESPN_REMAP(espn_name='Long Beach State Beach',
                          team_name='Long Beach St.',
                          nickname='Beach'),
               ESPN_REMAP(espn_name='Portland State Vikings',
                          team_name='Portland St.',
                          nickname='Vikings'),
               ESPN_REMAP(espn_name='Weber State Wildcats',
                          team_name='Weber St.',
                          nickname='Wildcats'),
               ESPN_REMAP(espn_name='Chicago State Cougars',
                          team_name='Chicago St.',
                          nickname='Cougars'),
               ESPN_REMAP(espn_name='Cleveland State Vikings',
                          team_name='Cleveland St.',
                          nickname='Vikings'),
               ESPN_REMAP(espn_name='Wright State Raiders',
                          team_name='Wright St.',
                          nickname='Raiders'),
               ESPN_REMAP(espn_name='Youngstown State Penguins',
                          team_name='Youngstown St.',
                          nickname='Penguins'),
               ESPN_REMAP(espn_name='Ball State Cardinals',
                          team_name='Ball St.',
                          nickname='Cardinals'),
               ESPN_REMAP(espn_name='Kent State Golden Flashes',
                          team_name='Kent St.',
                          nickname='Flashes'),
               ESPN_REMAP(espn_name='Coppin State Eagles',
                          team_name='Coppin St.',
                          nickname='Eagles'),
               ESPN_REMAP(espn_name='Delaware State Hornets',
                          team_name='Delaware St.',
                          nickname='Hornets'),
               ESPN_REMAP(espn_name='Morgan State Bears',
                          team_name='Morgan St.',
                          nickname='Bears'),
               ESPN_REMAP(espn_name='Norfolk State Spartans',
                          team_name='Norfolk St.',
                          nickname='Spartans'),
               ESPN_REMAP(espn_name='South Carolina State Bulldogs',
                          team_name='South Carolina St.',
                          nickname='Bulldogs'),
               ESPN_REMAP(espn_name='Illinois State Redbirds',
                          team_name='Illinois St.',
                          nickname='Redbirds'),
               ESPN_REMAP(espn_name='Indiana State Sycamores',
                          team_name='Indiana St.',
                          nickname='Sycamores'),
               ESPN_REMAP(espn_name='Missouri State Bears',
                          team_name='Missouri St.',
                          nickname='Bears'),
               ESPN_REMAP(espn_name='Murray State Racers',
                          team_name='Murray St.',
                          nickname='Racers'),
               ESPN_REMAP(espn_name='Boise State Broncos',
                          team_name='Boise St.',
                          nickname='Broncos'),
               ESPN_REMAP(espn_name='Colorado State Rams',
                          team_name='Colorado St.',
                          nickname='Rams'),
               ESPN_REMAP(espn_name='Fresno State Bulldogs',
                          team_name='Fresno St.',
                          nickname='Bulldogs'),
               ESPN_REMAP(espn_name='San Diego State Aztecs',
                          team_name='San Diego St.',
                          nickname='Aztecs'),
               ESPN_REMAP(espn_name='San José State Spartans',
                          team_name='San Jose St.',
                          nickname='Spartans'),
               ESPN_REMAP(espn_name='Utah State Aggies',
                          team_name='Utah St.',
                          nickname='Aggies'),
               ESPN_REMAP(espn_name='Morehead State Eagles',
                          team_name='Morehead St.',
                          nickname='Eagles'),
               ESPN_REMAP(espn_name='Southeast Missouri State Redhawks',
                          team_name='Southeast Missouri St.',
                          nickname='Redhawks'),
               ESPN_REMAP(espn_name='Tennessee State Tigers',
                          team_name='Tennessee St.',
                          nickname='Tigers'),
               ESPN_REMAP(espn_name='Arizona State Sun Devils',
                          team_name='Arizona St.',
                          nickname='Sun Devils'),
               ESPN_REMAP(espn_name='Oregon State Beavers',
                          team_name='Oregon St.',
                          nickname='Beavers'),
               ESPN_REMAP(espn_name='Washington State Cougars',
                          team_name='Washington St.',
                          nickname='Cougars'),
               ESPN_REMAP(espn_name='Mississippi State Bulldogs',
                          team_name='Mississippi St.',
                          nickname='Bulldogs'),
               ESPN_REMAP(espn_name='East Tennessee State Buccaneers',
                          team_name='East Tennessee St.',
                          nickname='Buccaneers'),
               ESPN_REMAP(espn_name='Northwestern State Demons',
                          team_name='Northwestern St.',
                          nickname='Demons'),
               ESPN_REMAP(espn_name='Alabama State Hornets',
                          team_name='Alabama St.',
                          nickname='Hornets'),
               ESPN_REMAP(espn_name='Alcorn State Braves',
                          team_name='Alcorn St.',
                          nickname='Braves'),
               ESPN_REMAP(espn_name='Jackson State Tigers',
                          team_name='Jackson St.',
                          nickname='Tigers'),
               ESPN_REMAP(espn_name='Mississippi Valley State Delta Devils',
                          team_name='Mississippi Valley St.',
                          nickname='Delta Devils'),
               ESPN_REMAP(espn_name='North Dakota State Bison',
                          team_name='North Dakota St.',
                          nickname='Bison'),
               ESPN_REMAP(espn_name='South Dakota State Jackrabbits',
                          team_name='South Dakota St.',
                          nickname='Jackrabbits'),
               ESPN_REMAP(espn_name='Appalachian State Mountaineers',
                          team_name='Appalachian St.',
                          nickname='Mountaineers'),
               ESPN_REMAP(espn_name='Arkansas State Red Wolves',
                          team_name='Arkansas St.',
                          nickname='Red Wolves'),
               ESPN_REMAP(espn_name='Georgia State Panthers',
                          team_name='Georgia St.',
                          nickname='Panthers'),
               ESPN_REMAP(espn_name='Texas State Bobcats',
                          team_name='Texas St.',
                          nickname='Bobcats'),
               ESPN_REMAP(espn_name='New Mexico State Aggies',
                          team_name='New Mexico St.',
                          nickname='Aggies'),

               ESPN_REMAP(espn_name='Charleston Cougars',
                          team_name='College of Charleston',
                          nickname='Cougars'),
               ESPN_REMAP(espn_name='Maine Black Bears',
                          team_name='Maine',
                          nickname='Blackbears'),
               ESPN_REMAP(espn_name='UMass Lowell River Hawks',
                          team_name='UMass Lowell',
                          nickname='River Hawks'),
               ESPN_REMAP(espn_name='Tulane Green Wave',
                          team_name='Tulane',
                          nickname='Green Wave'),
               ESPN_REMAP(espn_name='Tulsa Golden Hurricane',
                          team_name='Tulsa',
                          nickname='Golden Hurricane'),
               ESPN_REMAP(espn_name='UMass Minutemen',
                          team_name='Massachusetts',
                          nickname='Minutemen'),
               ESPN_REMAP(espn_name='Duke Blue Devils',
                          team_name='Duke',
                          nickname='Blue Devils'),
               ESPN_REMAP(espn_name='Georgia Tech Yellow Jackets',
                          team_name='Georgia Tech',
                          nickname='Yellow Jackets'),
               ESPN_REMAP(espn_name='Miami Hurricanes',
                          team_name='Miami FL',
                          nickname='Hurricanes'),
               ESPN_REMAP(espn_name='North Carolina Tar Heels',
                          team_name='North Carolina',
                          nickname='Tar Heels'),
               ESPN_REMAP(espn_name='Notre Dame Fighting Irish',
                          team_name='Notre Dame',
                          nickname='Fighting Irish'),
               ESPN_REMAP(espn_name='Wake Forest Demon Deacons',
                          team_name='Wake Forest',
                          nickname='Demon Deacons'),
               ESPN_REMAP(espn_name='TCU Horned Frogs',
                          team_name='TCU',
                          nickname='Horned Frogs'),
               ESPN_REMAP(espn_name='Texas Tech Red Raiders',
                          team_name='Texas Tech',
                          nickname='Red Raiders'),
               ESPN_REMAP(espn_name='DePaul Blue Demons',
                          team_name='DePaul',
                          nickname='Blue Demons'),
               ESPN_REMAP(espn_name='Marquette Golden Eagles',
                          team_name='Marquette',
                          nickname='Golden Eagles'),
               ESPN_REMAP(espn_name='St. John\'s Red Storm',
                          team_name='St. John\'s',
                          nickname='Red Storm'),
               ESPN_REMAP(espn_name='UConn Huskies',
                          team_name='Connecticut',
                          nickname='Huskies'),
               ESPN_REMAP(espn_name='Campbell Fighting Camels',
                          team_name='Campbell',
                          nickname='Fighting Camels'),
               ESPN_REMAP(espn_name='Gardner-Webb Runnin\' Bulldogs',
                          team_name='Gardner Webb',
                          nickname='Runnin\' Bulldogs'),
               ESPN_REMAP(espn_name='Presbyterian Blue Hose',
                          team_name='Presbyterian',
                          nickname='Blue Hose'),
               ESPN_REMAP(espn_name='South Carolina Upstate Spartans',
                          team_name='USC Upstate',
                          nickname='Spartans'),
               ESPN_REMAP(espn_name='Illinois Fighting Illini',
                          team_name='Illinois',
                          nickname='Fighting Illini'),
               ESPN_REMAP(espn_name='Minnesota Golden Gophers',
                          team_name='Minnesota',
                          nickname='Golden Gophers'),
               ESPN_REMAP(espn_name='Penn State Nittany Lions',
                          team_name='Penn St.',
                          nickname='Nittany Lions'),
               ESPN_REMAP(espn_name='Rutgers Scarlet Knights',
                          team_name='Rutgers',
                          nickname='Scarlet Knights'),
               ESPN_REMAP(espn_name='Hawai\'i Rainbow Warriors',
                          team_name='Hawaii',
                          nickname='Rainbow Warriors'),
               ESPN_REMAP(espn_name='Delaware Blue Hens',
                          team_name='Delaware',
                          nickname='Blue Hens'),
               ESPN_REMAP(espn_name='Florida International Panthers',
                          team_name='FIU',
                          nickname='Panthers'),
               ESPN_REMAP(espn_name='Middle Tennessee Blue Raiders',
                          team_name='Middle Tennessee',
                          nickname='Blue Raiders'),
               ESPN_REMAP(espn_name='North Texas Mean Green',
                          team_name='North Texas',
                          nickname='Mean Green'),
               ESPN_REMAP(espn_name='Detroit Mercy Titans',
                          team_name='Detroit',
                          nickname='Mercy Titans'),
               ESPN_REMAP(espn_name='Oakland Golden Grizzlies',
                          team_name='Oakland',
                          nickname='Golden Grizzlies'),
               ESPN_REMAP(espn_name='Canisius Golden Griffins',
                          team_name='Canisius',
                          nickname='Golden Griffins'),
               ESPN_REMAP(espn_name='Marist Red Foxes',
                          team_name='Marist',
                          nickname='Red Foxes'),
               ESPN_REMAP(espn_name='Niagara Purple Eagles',
                          team_name='Niagara',
                          nickname='Purple Eagles'),
               ESPN_REMAP(espn_name='Miami (OH) Redhawks',
                          team_name='Miami OH',
                          nickname='Rehawks'),
               ESPN_REMAP(espn_name='Nevada Wolf Pack',
                          team_name='Nevada',
                          nickname='Wolf Pack'),
               ESPN_REMAP(espn_name='Central Connecticut Blue Devils',
                          team_name='Central Connecticut',
                          nickname='Blue Devils'),
               ESPN_REMAP(espn_name="St. Francis (PA) Red Flash",
                          team_name='St. Francis PA',
                          nickname='Red Flash'),
               ESPN_REMAP(espn_name='St. Francis Brooklyn Terriers',
                          team_name='St. Francis NY',
                          nickname='Terriers'),
               ESPN_REMAP(espn_name="Tennessee Tech Golden Eagles",
                          team_name='Tennessee Tech',
                          nickname='Golden Eagles'),
               ESPN_REMAP(espn_name='UT Martin Skyhawks',
                          team_name='Tennessee Martin',
                          nickname='Skyhawks'),
               ESPN_REMAP(espn_name='California Golden Bears',
                          team_name='California',
                          nickname='Golden Bears'),
               ESPN_REMAP(espn_name='American University Eagles',
                          team_name='American',
                          nickname='Eagles'),
               ESPN_REMAP(espn_name='Army Black Knights',
                          team_name='Army',
                          nickname='Black Knights'),
               ESPN_REMAP(espn_name='Lehigh Mountain Hawks',
                          team_name='Lehigh',
                          nickname='Mountain Hawks'),
               ESPN_REMAP(espn_name='Loyola Maryland Greyhounds',
                          team_name='Loyola MD',
                          nickname='Greyhounds'),
               ESPN_REMAP(espn_name='Alabama Crimson Tide',
                          team_name='Alabama',
                          nickname='Crimson Tide'),
               ESPN_REMAP(espn_name='Ole Miss Rebels',
                          team_name='Mississippi',
                          nickname='Rebels'),
               ESPN_REMAP(espn_name='McNeese Cowboys',
                          team_name='McNeese St.',
                          nickname='Cowboys'),
               ESPN_REMAP(espn_name='Nicholls Colonels',
                          team_name='Nicholls St.',
                          nickname='Colonels'),
               ESPN_REMAP(espn_name='SE Louisiana Lions',
                          team_name='Southeastern Louisiana',
                          nickname='Lions'),
               ESPN_REMAP(espn_name='Texas A&M-Corpus Christi Islanders',
                          team_name='Texas A&M Corpus Chris',
                          nickname='Islanders'),
               ESPN_REMAP(espn_name='Arkansas-Pine Bluff Golden Lions',
                          team_name='Arkansas Pine Bluff',
                          nickname='Golden Lions'),
               ESPN_REMAP(espn_name='Grambling Tigers',
                          team_name='Grambling St.',
                          nickname='Tigers'),
               ESPN_REMAP(espn_name='North Dakota Fighting Hawks',
                          team_name='North Dakota',
                          nickname='Fighting Hawks'),
               ESPN_REMAP(espn_name='Oral Roberts Golden Eagles',
                          team_name='Oral Roberts',
                          nickname='Golden Eagles'),
               ESPN_REMAP(espn_name='Louisiana Ragin\' Cajuns',
                          team_name='Louisiana Lafayette',
                          nickname='Ragin\' Cajuns'),
               ESPN_REMAP(espn_name='Marshall Thundering Herd',
                          team_name='Marshall',
                          nickname='Thundering Herd'),
               ESPN_REMAP(espn_name='Southern Miss Golden Eagles',
                          team_name='Southern Miss',
                          nickname='Golden Eagles'),
               ESPN_REMAP(espn_name='UL Monroe Warhawks',
                          team_name='Louisiana Monroe',
                          nickname='Warhawks'),
               ESPN_REMAP(espn_name='Sam Houston Bearkats',
                          team_name='Sam Houston St.',
                          nickname='Bearkats'),
               ESPN_REMAP(espn_name='Seattle U Redhawks',
                          team_name='Seattle',
                          nickname='Redhawks'),
               ESPN_REMAP(espn_name='Tarleton Texans',
                          team_name='Tarleton St.',
                          nickname='Texans'),
               ESPN_REMAP(espn_name='Omaha Mavericks',
                          team_name='Nebraska Omaha',
                          nickname='Mavericks'),
               ESPN_REMAP(espn_name='Houston Christian Huskies',
                          team_name='Houston Baptist',
                          nickname='Huskies'),
               ESPN_REMAP(espn_name='Utah Tech Trailblazers',
                          team_name='Dixie St.',
                          nickname='Trailblazers'),
               ESPN_REMAP(espn_name='Purdue Fort Wayne Mastodons',
                          team_name='Fort Wayne',
                          nickname='Mastodons'),
               ESPN_REMAP(espn_name='Long Island University Sharks',
                          team_name='LIU Brooklyn',
                          nickname='Sharks'),
               ESPN_REMAP(espn_name='Kansas City Roos',
                          team_name='UMKC',
                          nickname='Roos'),
               ESPN_REMAP(espn_name='California Baptist Lancers',
                          team_name='Cal Baptist',
                          nickname='Lancers'),
               ESPN_REMAP(espn_name='',
                          team_name='',
                          nickname=''),


               ]

#  https│//en.wikipedia.org/w/index.php?title=List_of_NCAA_Division_I_basketball_arenas&action=edit&section=1
# Remove <ref>
stadium_fn = 'stadiums.csv'
STADIUM_RECORD = namedtuple('stadium_record', 'arena city state state_abbrev conf_name conf_short_name capacity opened')
CONF_REC = namedtuple('conference_record', 'name founded mens_sports womens_sports headquarter_city headquarter_state')

population_csv ='sub-est2021_all.csv'
population_original_columns = ['SUMLEV', 'STATE', 'COUNTY', 'PLACE', 'COUSUB', 'CONCIT', 'PRIMGEO_FLAG', 'FUNCSTAT', 'NAME', 'STNAME', 'ESTIMATESBASE2020', 'POPESTIMATE2020', 'POPESTIMATE2021']
population_columns = ['SUMLEV', 'STATE', 'COUNTY', 'PLACE', 'COUSUB', 'CONCIT', 'PRIMGEO_FLAG', 'FUNCSTAT', 'city_name', 'state_name', 'ESTIMATESBASE2020', 'POPESTIMATE2020', 'population']
assert len(population_original_columns) == len(population_columns)

teams_csv = 'cbb21.csv'
# https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset
teams_original_columns = ['TEAM', 'CONF', 'G', 'W', 'ADJOE', 'ADJDE', 'BARTHAG', 'EFG_O', 'EFG_D',  'TOR', 'TORD', 'ORB', 'DRB', 'FTR', 'FTRD', '2P_O', '2P_D', '3P_O',   '3P_D', 'ADJ_T', 'WAB', 'SEED']
teams_columns = ['team_name', 'conf_short_name', 'games_played', 'games_won', 'offensive_efficiency', 'defensive_efficiency', 'power_rating', 'field_goal_percentage_shot', 'field_goal_percentage_allowed', 'turnover_percentage', 'steal_rate', 'offensive_rebound_rate', 'offensive_rebound_allowed', 'free_throw_rate', 'free_throw_rate_allowed', 'two_point_shooting_percentage', 'two_point_shooting_percentage_allowed', 'three_point_shooting_percentage', 'three_point_shooting_allowed', 'tempo', 'wins_above_bubble', 'postseason_seed']
assert len(teams_original_columns) == len(teams_columns)

conferences = dict(A10=CONF_REC(name='Atlantic 10', founded=1979, mens_sports=8, womens_sports=10, headquarter_city='Newport News', headquarter_state='Virginia'),
                   ACC=CONF_REC(name='Atlantic Coast Conference', founded=1953, mens_sports=14, womens_sports=14, headquarter_city='Greensboro', headquarter_state='North Carolina'),
                   AE=CONF_REC(name='America East', founded=1979,mens_sports=10, womens_sports=12, headquarter_city='Boston', headquarter_state='Massachusetts'),
                   Amer=CONF_REC(name='American Athletic Conference', founded=1979, mens_sports=10, womens_sports=12, headquarter_city='Irving', headquarter_state='Texas'),
                   ASun=CONF_REC(name='ASUN',  founded=1978, mens_sports=10, womens_sports=11, headquarter_city='Atlanta', headquarter_state='Georgia'),
                   B10=CONF_REC(name='Big Ten', founded=1896, mens_sports=14, womens_sports=14, headquarter_city='Rosemont', headquarter_state='Illinois'),
                   B12=CONF_REC(name='Big 12', founded=1994, mens_sports=10, womens_sports=10, headquarter_city='Irving', headquarter_state='Texas'),
                   BE=CONF_REC(name='Big East', founded=1979, mens_sports=11, womens_sports=11, headquarter_city='New York', headquarter_state='New York'),
                   BSky=CONF_REC(name='Big Sky',founded=1969, mens_sports=7, womens_sports=9, headquarter_city='Farmington', headquarter_state='Utah'),
                   BSth=CONF_REC(name='Big South', founded=1983, mens_sports=10, womens_sports=10, headquarter_city='Charlotte', headquarter_state='North Carolina'),
                   BW=CONF_REC(name='Big West', founded=1969, mens_sports=8, womens_sports=10, headquarter_city='Irvine', headquarter_state='California'),
                   CAA=CONF_REC(name='Colonial Athletic Association', founded=1995, mens_sports=11, womens_sports=11, headquarter_city='Richmond', headquarter_state='Virginia'),
                   CUSA=CONF_REC(name='Conference USA', founded=1979, mens_sports=10, womens_sports=11, headquarter_city='Dallas', headquarter_state='Texas'),
                   Horz=CONF_REC(name='Horizon League', founded=1979, mens_sports=10, womens_sports=11, headquarter_city='Indianapolis', headquarter_state='Indiana'),
                   Ivy=CONF_REC(name='Ivy League', founded=1954, mens_sports=17, womens_sports=16, headquarter_city='Princeton', headquarter_state='New Jersey'),
                   MAAC=CONF_REC(name='Metro Atlantic Athletic Conference', founded=1980, mens_sports=11, womens_sports=13, headquarter_city='Edison', headquarter_state='New Jersey'),
                   MAC=CONF_REC(name='Mid-American Conference',founded=1946, mens_sports=11, womens_sports=13, headquarter_city='Cleveland', headquarter_state='Ohio'),
                   MEAC=CONF_REC(name='Mid-Eastern Athletic Conference', founded=1907, mens_sports=7, womens_sports=10, headquarter_city='Norfolk', headquarter_state='Virginia'),
                   MVC=CONF_REC(name='Missouri Valley Conference', founded=1907, mens_sports=7, womens_sports=10, headquarter_city='St. Louis', headquarter_state='Missouri'),
                   MWC=CONF_REC(name='Mountain West', founded=1998, mens_sports=8, womens_sports=10, headquarter_city='Colorado Springs', headquarter_state='Colorado'),
                   NEC=CONF_REC(name='Northeast Conference', founded=1981, mens_sports=11, womens_sports=13, headquarter_city='Somerset', headquarter_state='New Jersey'),
                   OVC=CONF_REC(name='Ohio Valley Conference', founded=1948, mens_sports=7, womens_sports=10, headquarter_city='Brentwood', headquarter_state='Tennessee'),
                   P12=CONF_REC(name='Pac-12', founded=1915, mens_sports=11, womens_sports=13, headquarter_city='San Francisco', headquarter_state='California'),
                   Pat=CONF_REC(name='Patriot League', founded=1986, mens_sports=11, womens_sports=13, headquarter_city='Bethlehem', headquarter_state='Pennsylvania'),
                   SB=CONF_REC(name='Sun Belt', founded=1976, mens_sports=9, womens_sports=9, headquarter_city='New Orleans', headquarter_state='Louisiana'),
                   SC=CONF_REC(name='Southern Conference', founded=1921, mens_sports=11, womens_sports=9, headquarter_city='Spartanburg', headquarter_state='South Carolina'),
                   SEC=CONF_REC(name='Southeastern Conference', founded=1932, mens_sports=9, womens_sports=12, headquarter_city='Birmingham', headquarter_state='Alabama'),
                   Slnd=CONF_REC(name='Southland Conference', founded=1996, mens_sports=8, womens_sports=10, headquarter_city='Frisco', headquarter_state='Texas'),
                   Sum=CONF_REC(name='Summit League', founded=1982, mens_sports=9, womens_sports=10, headquarter_city='Sioux Falls', headquarter_state='South Dakota'),
                   SWAC=CONF_REC(name='Southwestern Athletic Conference', founded=1920, mens_sports=8, womens_sports=10, headquarter_city='Birmingham', headquarter_state='Alabama'),
                   WAC=CONF_REC(name='Western Athletic Conference', founded=1962, mens_sports=10, womens_sports=10, headquarter_city='Arlington', headquarter_state='Texas'),
                   WCC=CONF_REC(name='West Coast Conference', founded=1942, mens_sports=6, womens_sports=9, headquarter_city='San Mateo', headquarter_state='California'))
print(f'There are {len(conferences)} conferences')


stadiums = {}
with open(stadium_fn, 'r', encoding='utf-8') as fid:
    line = fid.readline()
    while line[0:2] != '|-':
        line = fid.readline()
    columns = [x.strip() for x in line[2:].split('!!')]
    assert len(columns) == 8 # Image, Arena, City, State, Team, Conference, Capacity, Opened

    line = fid.readline()
    while line:
        while line == '|-\n':
            line = fid.readline()  # Ignore stadium image

        arena = fid.readline().replace('[', '').replace(']', '').replace('|', '')
        if 'File:' in arena or 'Image:' in arena or '\n' == arena or '|-style' in arena:
            arena = fid.readline().replace('[', '').replace(']', '').replace('|', '')

        line = fid.readline().replace('[', '').replace(']', '')[1:]
        city = line.split('|')[-1]

        line = fid.readline().replace('[', '').replace(']', '')[1:]
        state, state_abbrev = line.split('|')

        line = fid.readline().replace('[', '').replace(']', '')[1:]
        if 'Saint Bonaventure' in line:
            team_name, team_sort_name = 'Saint Bonaventure', 'St. Bonaventure Bonnies'
        elif 'Hawaii Rainbow Warriors basketball|Hawaii men' in line:
            team_name, team_sort_name = 'Hawaii Rainbow Warriors', 'Hawaii Rainbow Wahine'
        else:
            team_name, team_short_name = line.split('|')
        if team_name.strip() == "Memphis Tigers men's basketball":
            team_name, team_short_name = 'Memphis Tigers', ''

        line = fid.readline().replace('[', '').replace(']', '')[1:]
        if "American Athletic Conference" in line:
            conf_name = 'American Athletic Conference'
            conf_short_name = 'American'
        elif "ASUN Conference" in line:
            conf_name = 'ASUN Conference'
            conf_short_name = 'ASUN'
        elif "Big 12 Conference" in line:
            conf_name = 'Big 12 Conference'
            conf_short_name = 'Big 12'
        elif "Independent" in line:
            conf_name = 'Independent'
            conf_short_name = 'Independent'
        elif "Conference TBA" in line:
            conf_name = 'Conference TBA'
            conf_short_name = 'TBA'
        elif "Conference USA" in line:
            conf_name = 'Conference USA'
            conf_short_name = 'USA'
        else:
            try:
                conf_name, conf_short_name = line.split('|')
            except:
                print(line)
                pdb.set_trace()
                raise

        line = fid.readline().replace('[', '').replace(']', '').replace('|', '')[1:]
        if 'Bellarmine currently lists this as the basketball capacity' in line:
            capacity = 18252
        elif 'cite webtitle=The Nest' in line:
            capacity = 1012
        elif 'McCann Arenawebsite=GoRedFoxes.com' in line:
            opened = 1977
        else:
            try:
                capacity = int(line.replace(',', ''))
            except:
                print(line)
                raise

        line = fid.readline().replace('[', '').replace(']', '').replace('|', '')[1:]
        if 'Moody Center' in line:
            opened = 2022
        elif 'High Point University arena project delayed for a year' in line:
            opened = 2021
        elif 'Manhattan College Enhances Draddy Gymnasium' in line:
            opened = 1978
        elif '205241110.aspxtitle=McCann Arenawebsite=GoRedFoxes.com' in line:
            opened = 1977
        elif 'Idaho move ahead with its unique arena first' in line:
            opened = 2021
        else:
            try:
                opened = int(line)
            except:
                print(line)
                raise

        line = fid.readline() # Ignore |-

        team_short_name = team_short_name.strip()
        stadium_record = STADIUM_RECORD(arena=arena.strip(),
                                        city=city.strip(),
                                        state=state.strip(),
                                        state_abbrev=state_abbrev.strip(),
                                        conf_name=conf_name.strip(),
                                        conf_short_name=conf_short_name.strip(),
                                        capacity=capacity,
                                        opened=opened)
        assert team_short_name not in stadiums, f'Team {team_short_name} already in stadiums \n{stadiums[team_short_name]}\n{stadium_record}'
        stadiums[team_short_name] = stadium_record
print(f'There are {len(stadiums)} stadium records')

teams_df = pd.read_csv(teams_csv)
assert np.all(teams_original_columns == teams_df.columns), 'Check of columns matching failed'
teams_df.columns = teams_columns
print(f'There are {len(teams_df)} teams in the csv file and {len(stadiums)} in the stadiums file')
for tn in teams_df.team_name:
    if tn not in stadiums:
        # print(f'Team {tn} in csv file but not in stadiums')
        teams_df = teams_df[teams_df.team_name != tn]
print(f'There are {len(teams_df)} teams in the csv file and {len(stadiums)} in the stadiums file')
print()
for tn in sorted(stadiums.keys()):
    if not np.any(teams_df.team_name == tn):
        # print(f'Team {tn} in stadiums but not in csv')
        del stadiums[tn]
print(f'There are {len(teams_df)} teams in the csv file and {len(stadiums)} in the stadiums file')

population_df = pd.read_csv(population_csv, encoding="ISO-8859-1")
population_df.columns = population_columns
populations = {}
# population_df[population_df.city_name == 'Auburn city'][population_df.state_name == 'Alabama']
# For each team name, find the population of the city/town the stadium is in
population = {}
for tn in teams_df.team_name:
    # City names have city, township, or town appended to it
    if stadiums[tn].city == 'Lexington' and stadiums[tn].state == 'Kentucky':
        city_selector = population_df.city_name == 'Lexington-Fayette urban county'
    elif stadiums[tn].city == 'Macon' and stadiums[tn].state == 'Georgia':
        city_selector = population_df.city_name == 'Macon-Bibb County'
    elif stadiums[tn].city == 'Nashville' and stadiums[tn].state == 'Tennessee':
        city_selector = population_df.city_name == 'Nashville-Davidson metropolitan government'
    elif stadiums[tn].city == 'Athens' and stadiums[tn].state == 'Georgia':
        city_selector = population_df.city_name == 'Athens-Clarke County unified government'
    elif stadiums[tn].city == 'Louisville' and stadiums[tn].state == 'Kentucky':
        city_selector = population_df.city_name == 'Louisville/Jefferson County metro government'
    else:
        city_selector = (population_df.city_name == f'{stadiums[tn].city} city') |\
                        (population_df.city_name == f'{stadiums[tn].city} township') | \
                        (population_df.city_name == stadiums[tn].city) | \
                        (population_df.city_name == f'{stadiums[tn].city} village') | \
                        (population_df.city_name == f'{stadiums[tn].city} County') | \
                        (population_df.city_name == f'{stadiums[tn].city} borough') | \
                        (population_df.city_name == f'{stadiums[tn].city} town')
    assert np.any(city_selector), f'{tn}\'s stadium in {stadiums[tn].city} is not in {population_csv}'
    state_selector = population_df.state_name == stadiums[tn].state
    assert np.any(state_selector), f'{tn}\'s stadium in {stadiums[tn].state} is not in {population_csv}'
    assert np.any(city_selector & state_selector), f'{tn}\'s stadium in {stadiums[tn].city}, {stadiums[tn].state} is not in {population_csv}'
    population[tn] = population_df[city_selector & state_selector].population.max()
    # print(f'{tn} plays in {stadiums[tn].arena} located in {stadiums[tn].city}, {stadiums[tn].state}',
    #       f'which has a population of {population[tn]}')

for k,v in conferences.items():
    city_selector = (population_df.city_name == f'{v.headquarter_city} city') |\
                    (population_df.city_name == f'{v.headquarter_city} township') | \
                    (population_df.city_name == v.headquarter_city) | \
                    (population_df.city_name == f'{v.headquarter_city} village') | \
                    (population_df.city_name == f'{v.headquarter_city} County') | \
                    (population_df.city_name == f'{v.headquarter_city} borough') | \
                    (population_df.city_name == f'{v.headquarter_city} town')
    assert np.any(city_selector), f'{k}\'s city in {v.headquarter_city} is not in {population_csv}'
    state_selector = population_df.state_name == v.headquarter_state
    assert np.any(state_selector), f'{k}\'s state in {v.headquarter_state} is not in {population_csv}'
    assert np.any(city_selector & state_selector), f'{k}\'s stadium in {v.headquarter_city}, {v.headquarter_state} is not in {population_csv}'
    population[v.name] = population_df[city_selector & state_selector].population.max()


# Remove the old databases
conns = []
for db in DATABASES:
    if os.path.exists(db):
        os.remove(db)
    conn = sqlite3. connect(db)
    conn.row_factory = sqlite3.Row
    conn.cursor().execute('PRAGMA foreign_keys = ON')
    conns.append(conn)

# Set up the Stadiums
for index, conn in enumerate(conns):
    with closing(conn.cursor()) as cursor:
        cursor.execute('''
               CREATE TABLE Locations
                  (location_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city TEXT,
                   state TEXT,
                   population INTEGER,
                   UNIQUE (city, state))''')
        cursor.execute('''
               CREATE TABLE Stadiums
                  (stadium_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   location_id REFERENCES Locations(location_id),
                   capacity INTEGER,
                   year_opened INTEGER)''')
        cursor.execute('''
               CREATE TABLE Conferences
                  (conference_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,              -- Like Atlantic Coast Conference
                   short_name TEXT,        -- 3 to 5 letters like ACC
                   year_founded INTEGER,
                   number_mens_sports INTEGER UNSIGNED,
                   number_womens_sports INTEGER UNSIGNED,
                   location_id REFERENCES Locations(location_id), -- headquarter location
                   UNIQUE(name))''')
        cursor.execute('''
               CREATE TABLE Teams
                  (team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT,
                   nickname TEXT DEFAULT NULL,
                   conference_id REFERENCES Conferences(conference_id),
                   stadium_id REFERENCES Stadiums(stadium_id),
                   games_played INTEGER, -- # games played in 2020
                   games_won INTEGER,    -- # games won in 2020 
                   power_rating FLOAT,   -- # Power Rating (Chance of beating an average Division I team)
                   field_goal_percentage FLOAT,         -- 0.0 to 100.0
                   field_goal_percentage_allowed FLOAT, -- 0.0
                   turn_over_rate FLOAT,                -- 0.0 to 100.0
                   steal_rate FLOAT,
                   offensive_rebound_rate FLOAT,
                   offensive_rebound_rate_allowed FLOAT,
                   two_point_percentage FLOAT,
                   two_point_allowed_percentage FLOAT,
                   three_point_percentage FLOAT,
                   three_point_allowed_percentage FLOAT,
                   wins_above_bubble FLOAT)   ''')
        cursor.execute('''
              CREATE TABLE Players
                 (player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  team_id REFERENCES Teams(team_id),
                  first_name TEXT,
                  last_name TEXT,   -- contains no blanks
                  number INTEGER,
                  position TEXT,
                  height INTEGER,   -- in inches; NULL if no information available
                  weight INTEGER    -- in pounds; NULL if no information available
                  )''')

        # Insert the conferences
        for k,v in conferences.items():
            cursor.execute('''
                    SELECT location_id 
                      FROM Locations
                     WHERE city=:city AND
                           state=:state''',
                           dict(city=v.headquarter_city,
                                state=v.headquarter_state))
            location_id = cursor.fetchone()
            if not location_id or not location_id['location_id']:
                cursor.execute('''
                        INSERT INTO Locations (city,   state,  population)
                                       VALUES (:city, :state, :population)
                        RETURNING location_id''',
                               dict(city=v.headquarter_city,
                                    state=v.headquarter_state,
                                    population=population[v.name]))
                location_id = cursor.fetchone()
            location_id=location_id['location_id']
            # print(f'{v.headquarter_city}, {v.headquarter_state} has population of {population[v.name]} and is location {location_id}')

            cursor.execute('''
                    INSERT INTO Conferences ( name,  short_name,  year_founded,  number_mens_sports,  number_womens_sports,  location_id)
                                     VALUES (:name, :short_name, :year_founded, :number_mens_sports, :number_womens_sports, :location_id)  ''',
                           dict(name=v.name,
                                short_name=k,
                                number_mens_sports=v.mens_sports,
                                number_womens_sports=v.womens_sports,
                                location_id=location_id,
                                year_founded=v.founded))

        # Insert the stadiums
        for index, row in teams_df.iterrows():
            cursor.execute('''
                    SELECT location_id 
                      FROM Locations
                     WHERE city=:city AND
                           state=:state''',
                           dict(city=stadiums[row.team_name].city,
                                state=stadiums[row.team_name].state))
            location_id = cursor.fetchone()
            if not location_id or not location_id['location_id']:
                cursor.execute('''
                        INSERT INTO Locations (city,   state,  population)
                                       VALUES (:city, :state, :population)
                        RETURNING location_id''',
                               dict(city=stadiums[row.team_name].city,
                                    state=stadiums[row.team_name].state,
                                    population=population[row.team_name]))
                location_id = cursor.fetchone()
            location_id=location_id['location_id']
            # print(f'{stadiums[row.team_name].city}, {stadiums[row.team_name].state} has population of {population[row.team_name]} and is location {location_id}')

            cursor.execute('''
                    INSERT INTO Stadiums ( name,  year_opened,  location_id,  capacity)
                                  VALUES (:name, :year_opened, :location_id, :capacity) 
                           RETURNING stadium_id''',
                           dict(name=stadiums[row.team_name].arena,
                                location_id=location_id,
                                capacity=stadiums[row.team_name].capacity,
                                year_opened=stadiums[row.team_name].opened))
            stadium_id = cursor.fetchone()['stadium_id']
            cursor.execute('''SELECT conference_id FROM Conferences where name = :name''',
                           dict(name=conferences[row.conf_short_name].name))
            conference_id = cursor.fetchone()['conference_id']
            cursor.execute('''
                    INSERT INTO Teams (name, conference_id, games_played, games_won, power_rating,
                                       field_goal_percentage, field_goal_percentage_allowed,
                                       turn_over_rate, steal_rate, offensive_rebound_rate,
                                       offensive_rebound_rate_allowed, two_point_percentage,
                                       two_point_allowed_percentage, three_point_percentage,
                                       three_point_allowed_percentage, wins_above_bubble,
                                       stadium_id)
                               VALUES (:name, :conference_id, :games_played, :games_won, :power_rating,
                                       :field_goal_percentage, :field_goal_percentage_allowed,
                                       :turn_over_rate, :steal_rate, :offensive_rebound_rate,
                                       :offensive_rebound_rate_allowed, :two_point_percentage,
                                       :two_point_allowed_percentage, :three_point_percentage,
                                       :three_point_allowed_percentage, :wins_above_bubble,
                                       :stadium_id)  ''',
                           dict(name=row.team_name, conference_id=conference_id, games_played=row.games_played, games_won=row.games_won, power_rating=row.power_rating,
                                field_goal_percentage=row.field_goal_percentage_shot, field_goal_percentage_allowed=row.field_goal_percentage_allowed,
                                turn_over_rate=row.turnover_percentage, steal_rate=row.steal_rate, offensive_rebound_rate=row.offensive_rebound_rate,
                                offensive_rebound_rate_allowed=row.offensive_rebound_allowed, two_point_percentage=row.two_point_shooting_percentage,
                                two_point_allowed_percentage=row.two_point_shooting_percentage_allowed, three_point_percentage=row.three_point_shooting_percentage,
                                three_point_allowed_percentage=row.three_point_shooting_percentage, wins_above_bubble=row.wins_above_bubble,
                                stadium_id=stadium_id))

    conn.commit()


def get_team_ids(cursors, team_name):
    '''Given a team name, find the team id from both databases
       as a side effect, if the nickname is known, update it'''
    team_name_split = team_name.split(' ')
    if team_name in MISSING_TEAMS:
        return []

    for espn_remap in REMAP_TEAMS:
        if team_name == espn_remap.espn_name:
            team_ids = []
            for cursor in cursors:
                cursor.execute('''SELECT team_id FROM Teams WHERE name=:name''',
                               dict(name=espn_remap.team_name))
                try:
                    team_ids.append(cursor.fetchone()['team_id'])
                except:
                    pdb.set_trace()
                cursor.execute('''UPDATE Teams SET nickname=:nickname WHERE name=:name''',
                               dict(name=espn_remap.team_name,
                                    nickname=espn_remap.nickname))
                cursor.connection.commit()
            return team_ids
    if 'State' in team_name:
        print(f'JJM update ESPN_REMAP with {team_name}')
        team_ids = get_team_ids(cursors, team_name.replace('State', 'St.'))
        if len(team_ids) == 2:
            return team_ids
    team_ids = []
    for cursor in cursors:
        cursor.execute('''SELECT name, team_id
                           FROM Teams
                          WHERE name = :name''',
                   dict(name=team_name,
                        name2=' '.join(team_name_split[:-1])))
        rows = cursor.fetchall()
        if not rows:
            cursor.execute('''SELECT name, team_id
                               FROM Teams
                              WHERE name = :name''',
                       dict(name=' '.join(team_name_split[:-1])))
            rows = cursor.fetchall()
            if rows and len(rows) == 1:
                cursor.execute('''UPDATE Teams SET nickname=:nickname WHERE name=:name''',
                               dict(name=' '.join(team_name_split[:-1]),
                                    nickname=team_name_split[-1]))
                cursor.connection.commit()
        if not rows:
            print(f'Team name {team_name} not in SQLite {cursors.index(cursor)}')
            team_ids = []
        elif len(rows) != 1:
            print(f'Team name {team_name} appears twice in SQLite {cursors.index(cursor)}')
            team_ids = []
        else:
            team_ids.append(rows[0]['team_id'])
    return team_ids

# Propogate players
confs = {}

url = f"{URL_BASE}/mens-college-basketball/teams"
r = requests.get(url, allow_redirects=False)
if r.status_code == 200:
    # parser.feed(r.text)
    soup = BeautifulSoup(r.text, 'html.parser')
    cursors = []
    for conn in conns:
        cursors.append(conn.cursor())

    # confs are mt7
    for conf_tag in soup.find_all("div", class_="mt7"):
        conf_name = conf_tag.find("div", "headline").text
        if conf_name == 'ACC':
            conf_name = 'Atlantic Coast Conference'
        if conf_name == 'MAAC':
            conf_name = 'Metro Atlantic Athletic Conference'
        if conf_name == 'MEAC':
            conf_name = 'Mid-Eastern Athletic Conference'
        if conf_name == 'SEC':
            conf_name = 'Southeastern Conference'
        if conf_name == 'SWAC':
            conf_name = 'Southwestern Athletic Conference'
        if conf_name == 'WAC':
            conf_name = 'Western Athletic Conference'
        if conf_name == 'Colonial':
            conf_name = 'Colonial Athletic Association'
        if conf_name in ['American']:
            conf_name += ' Athletic Conference'
        if conf_name in ['Horizon', 'Ivy']:
            conf_name += ' League'
        if conf_name in ['Northeast', 'Missouri Valley', 'Ohio Valley', 'Mid-American', 'Southern', 'West Coast Conference']:
            conf_name += ' Conference'


        confs[conf_name] = {}
        for team_tag in conf_tag.find_all("div", class_="mt3"):
            team_name = team_tag.find("h2").text
            if team_name in MISSING_TEAMS:
                continue
            team_ids = get_team_ids(cursors, team_name)
            if len(team_ids) != 2:
                print(f'Team not found "{team_name}"')
                # import pdb; pdb.set_trace()
                continue
            confs[conf_name][team_name] = {}
            for href_tag in team_tag.find_all("a", href=True):
                if href_tag['href'].find('/roster/') > -1:
                    roster = confs[conf_name][team_name]['roster'] = {}
                    t = requests.get(f"{URL_BASE}{href_tag['href']}", allow_redirects=False)
                    if t.status_code == 200:
                        team_soup = BeautifulSoup(t.text, 'html.parser')
                        roster_tag = team_soup.find('div', class_="ResponsiveTable Team Roster")
                        table_tag = roster_tag.find('tbody', class_="Table__TBODY")
                        for row in table_tag.find_all('tr'):
                            cols = row.find_all('td')
                            # Name number is in index 1, position 2,
                            name = cols[1].find('a').text.split(' ')
                            first_name = ' '.join(name[:-1])
                            last_name = name[-1]
                            if cols[1].find('span') is None:
                                number = None
                            else:
                                number = cols[1].find('span').text
                            height = cols[3].text.replace('"', '').replace("'", "")
                            height = height.split(" ")
                            try:
                                height = 12 * int(height[0]) + int(height[1])
                            except:
                                height = None
                            try:
                                weight = int(cols[4].text.split(' ')[0])
                            except:
                                weight = None
                            # roster[name] = dict(number=number,
                            #                     position=cols[2].text,
                            #                     height=cols[3].text,
                            #                     weight=cols[4].text)
                            if len(team_ids) > 0:
                                for cursor in cursors:
                                    cursor.execute('''
                                          INSERT INTO Players (team_id, first_name, last_name, number, position, height, weight)
                                                      VALUES(:team_id, :first_name, :last_name, :number, :position,:height, :weight)''',
                                                   dict(team_id=team_ids[cursors.index(cursor)],
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        number=number,
                                                        position=cols[2].text,
                                                        height=height,
                                                        weight=weight))
    for conn in conns:
        conn.commit()

# Make the databases different
with closing(conn.cursor()) as cursor:
    # A conference with no teams
    cursor.execute('''
          INSERT INTO Conferences ( name, short_name, year_founded, number_mens_sports, number_womens_sports,  location_id)
                           VALUES ('UNC Computer Science', 'UNC_CS', 1962, 0, 1, 2)   ''')
    # Stadium with no team
    cursor.execute('''
          INSERT INTO Stadiums ( name,  year_opened,  location_id,  capacity)
                        VALUES ('Brooks Hall', 1980, (SELECT location_id FROM Locations where city='Chapel Hill' AND state='North Carolina'), 575)''')

    cursor.execute('''
          INSERT INTO Locations (city,   state,  population)
                         VALUES (:city, :state, :population)
                      RETURNING location_id''',
                   dict(city='Ashley', state='PA', population=2581))
    location_id = cursor.fetchone()
    location_id=location_id['location_id']

    cursor.execute('''
          INSERT INTO Stadiums ( name,  year_opened,  location_id,  capacity)
                        VALUES (:name, :year_opened, :location_id, :capacity) 
                     RETURNING stadium_id''',
                   dict(name='Huber Breaker',
                        location_id=location_id,
                        capacity=816,
                        year_opened=1938))
    stadium_id = cursor.fetchone()['stadium_id']
    cursor.execute('''
          INSERT INTO Conferences ( name, short_name, year_founded, number_mens_sports, number_womens_sports,  location_id)
                           VALUES ('Coal pickers', 'Pickers', 1855, 1, 0, :location_id)
                     RETURNING conference_id ''',
                   dict(location_id=location_id))
    conference_id = cursor.fetchone()['conference_id']
    cursor.execute('''
            INSERT INTO Teams (name, nickname, conference_id, games_played, games_won, power_rating,
                               field_goal_percentage, field_goal_percentage_allowed,
                               turn_over_rate, steal_rate, offensive_rebound_rate,
                               offensive_rebound_rate_allowed, two_point_percentage,
                               two_point_allowed_percentage, three_point_percentage,
                               three_point_allowed_percentage, wins_above_bubble,
                               stadium_id)
                       VALUES ('Hanover', 'Hawkeyes', :conference_id, 9, 5, -1,
                               .05, .99,
                               .45, .55, .10,
                               .45, .6,
                               .7, .3,
                               .5, 5,
                               :stadium_id) 
                       RETURNING team_id   ''',
                   dict(conference_id=conference_id,
                        stadium_id=stadium_id))
    cursor.execute('''
            INSERT INTO Teams (name, nickname, conference_id, games_played, games_won, power_rating,
                               field_goal_percentage, field_goal_percentage_allowed,
                               turn_over_rate, steal_rate, offensive_rebound_rate,
                               offensive_rebound_rate_allowed, two_point_percentage,
                               two_point_allowed_percentage, three_point_percentage,
                               three_point_allowed_percentage, wins_above_bubble,
                               stadium_id)
                       VALUES ('Ashley', 'Rockets', :conference_id, 10, 5, -1,
                               .05, .99,
                               .45, .55, .10,
                               .45, .6,
                               .7, .3,
                               .5, 5,
                               :stadium_id) 
                       RETURNING team_id   ''',
                   dict(conference_id=conference_id,
                        stadium_id=stadium_id))
    team_id = cursor.fetchone()['team_id']
    cursor.execute('''
          INSERT INTO Players (team_id, first_name, last_name, number, position, height, weight)
                      VALUES(:team_id, 'Brad', 'Daugherty', 42, 'F', 82, 220)''',
                   dict(team_id=team_id))
    cursor.execute('''
          INSERT INTO Players (team_id, first_name, last_name, number, position, height, weight)
                      VALUES(:team_id, 'David', 'Popson', 35, 'C', 85, 220)''',
                   dict(team_id=team_id))
    cursor.execute('''
          INSERT INTO Players (team_id, first_name, last_name, number, position, height, weight)
                      VALUES(:team_id, 'Joe', 'Wolf', 24, 'F', 83, 275)''',
                   dict(team_id=team_id))
    cursor.execute('''
          INSERT INTO Players (team_id, first_name, last_name, number, position, height, weight)
                      VALUES(:team_id, 'Kennedy', 'Meeks', 3, 'PF', 82, 280)''',
                   dict(team_id=team_id))
    conn.commit()

# Get the schema
with closing(conns[0].cursor()) as cursor:
    cursor.execute('''SELECT sql
                        FROM sqlite_schema
                       WHERE type='table'  ''')
    schema = re.sub("\n  *",
                    "\n     ",
                    "\n".join([x[0] for x in cursor.fetchall()]))
    schema = re.sub(r'CREATE TABLE sqlite_sequence\(name,seq\)\n', '', schema)
    schema = re.sub('"Locations"', 'Locations', schema)
    schema = re.sub('"Stadiums"', 'Stadiums', schema)

    with open(DATABASES[0].replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
        json.dump(schema, fid)
