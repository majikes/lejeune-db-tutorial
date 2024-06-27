#!/usr/bin/python3
''' Run the grader against all possible submissions
    Can't do homeworks here '''

from contextlib import closing
from datetime import datetime, timedelta
from subprocess import Popen
from time import sleep

from COMP421.mypoll.src import db
from COMP421.mypoll.src.tools.DemoWorksheetBonus import bonus_date as demo_bonus_date
from COMP421.mypoll.src.tools.WelcomeWorksheetBonus import bonus_date as welcome_bonus_date
from assessments import updateGrades

while (True):
    for assessment in sorted(['game-nuclear-1', 'game-nuclear-2', 'game-nuclear-3', 'game-nuclear-4']):
        print(f'Running grader for {assessment}')
        with open(f'./{assessment}.log', 'a', encoding='utf-8') as out,\
                Popen(['./grade.py', f'key={assessment}'], stdout=out) as process:
            process.wait()
    print(f'Sleeping for one minute')
    sleep(60) 

