#!/usr/bin/env python3

# pip install us
import us

import csv
import sqlite3
import os

in_grader = 'setup' in os.getcwd()  # If in setup working directory, your in the grader

fnames = ['StatesA.sqlite', 'StatesB.sqlite']
for fname in fnames:
   if os.path.isfile(fname):
      os.remove(fname)

# https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/state/detail/SCPRC-EST2019-18+POP-RES.csv
with open('SCPRC-EST2019-18+POP-RES.csv', 'r') as csvfile:
   reader = csv.DictReader(csvfile, skipinitialspace=True)
   population = {}
   for row in reader:
      population[row['NAME']] = row

population['American Samoa'] = dict(POPESTIMATE2019='55312')
population['Guam'] = dict(POPESTIMATE2019='55312')
population['Northern Mariana Islands'] = dict(POPESTIMATE2019='57216')
population['Puerto Rico'] = dict(POPESTIMATE2019='3285874')
population['Virgin Islands'] = dict(POPESTIMATE2019='106631')

connA = sqlite3.connect(fnames[0])
cursorA = connA.cursor()
connB = sqlite3.connect(fnames[1])
cursorB = connB.cursor()

create_table = '''
   CREATE table States (fid integer primary key,
                       name text,
                       abbreviation text,
                       is_territory integer, 
                       is_contiguous integer,
                       statehood_year integer, 
                       capital text,
                       time_zone text,
                       population integer)'''
cursorA.execute(create_table)
cursorB.execute(create_table)


for state in us.states.STATES_AND_TERRITORIES:
    fips = state.fips
    name = state.name
    abbreviation = state.abbr
    is_territory = state.is_territory
    is_contiguous = state.is_contiguous
    statehood_year = state.statehood_year
    capital = state.capital
    time_zone = state.capital_tz
    pop = int(population[name]['POPESTIMATE2019'])
    # print(f'{fips}: {name}/{abbreviation} is a {"territory" if is_territory else "state"}',
    #       f' {"is" if is_contiguous else "is not"} contiguous.',
    #       f' Capital {capital}. Time zone {time_zone}. Population {pop}')
    cursorA.execute('''
       INSERT INTO States (fid, name, abbreviation, is_territory, is_contiguous,
                           statehood_year, capital, time_zone, population)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   [state.fips, state.name, state.abbr, state.is_territory, state.is_contiguous,
                    state.statehood_year, state.capital, state.capital_tz, 
                    int(population[name]['POPESTIMATE2019'])])
    # StatesB does not have california or any territories
    if state.name != 'California' and not state.is_territory:
       cursorB.execute('''
          INSERT INTO States (fid, name, abbreviation, is_territory, is_contiguous,
                              statehood_year, capital, time_zone, population)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      [state.fips, state.name, state.abbr, state.is_territory, state.is_contiguous,
                       state.statehood_year, state.capital, state.capital_tz, 
                       int(population[name]['POPESTIMATE2019'])])
connA.commit()
connB.commit()
cursorA.execute(''' SELECT count(*) from States''')
assert cursorA.fetchone()[0] == 55
cursorB.execute(''' SELECT count(*) from States''')
assert cursorB.fetchone()[0] == 49
