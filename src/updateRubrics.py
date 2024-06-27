#! /usr/bin/python3
"""Get the rubrics from the templates into the db"""
# pylint: disable=too-many-nested-blocks
# pylint: disable=too-many-branches, unsupported-membership-test, too-many-statements, bad-indentation

import contextlib
import json
import math
import os.path as osp
import re
import sys
from datetime import datetime
from glob import glob

import dotenv

import Args
import bottle
from appbase import static
from config import assessment_folders, assessment_types
from evalInContext import evalMultiple
from inputs import inputs

dotenv.load_dotenv()
# Add class directory to template directory
bottle.TEMPLATE_PATH.append('./md-includes/')
bottle.TEMPLATE_PATH = list(dict.fromkeys(bottle.TEMPLATE_PATH))

try:
   import db
except ModuleNotFoundError:
   print("no db module")
   sys.exit(0)

args = Args.Parse(force=0, local=0, verbose=0)

# Dummy functions
bottle.SimpleTemplate.defaults["get_url"] = lambda x, **y: x
bottle.SimpleTemplate.defaults["linkable_header"] = lambda y: y
bottle.SimpleTemplate.defaults["static"] = static


def json_converter(obj):
   """ JSON override for datetime objects"""
   if isinstance(obj, datetime):
      return str(obj)
   return None

def getRubrics(path, cursor):
   """Get the rubric from a template"""
   # pylint: disable=possibly-unused-variable

   # Set up local variables for bottle.template
   key = path.split("/")[-1].split(".")[0]
   inp = inputs(key)
   pages = []
   section = '003'
   seeAllQuestions = True
   exam_time = datetime(2021, 12, 7, 12, 0, 0)
   team_number = 0
   team_member_number = 0
   conflict_exam = False
   rid = 1
   question_pool_number = 1
   cursor.execute("select onyen from roll")
   onyens = [row.onyen for row in cursor.fetchall()]

   # The path may actually be a itmd file.  Get the path of the tmd file
   index = path.find(key)
   tmd_path = f'{path[:index]}{key}.tmd'

   # Silly change in Fall 2023, don't have a line `% if 'questions' in pages`
   # It will make your new worksheet have no questions!
   pattern = re.compile(r'% *if *[\'\"]questions[\'\"] *in *pages *:')
   with open(tmd_path, 'r', encoding='utf-8') as fid:
      for i, line in enumerate(fid):
         assert pattern.search(line) is None, f'For file {tmd_path}, line {i+1} with test of questions in pages is deprecated'


   # Render assuming no pages, but re-render w/ pages to get all the info
   bottle.template(tmd_path, constant_e=math.e, constant_pi=math.pi, log=math.log,
                   get_url=lambda x, **y: x, **inp.env(), **locals(), **dotenv.dotenv_values())
   pages = inp.info.get('pages', [])
   assessment_type = inp.info.get('assessment_type', None)
   assert assessment_type in assessment_types, \
       f"{tmd_path} has assssment type {assessment_type} which is not in {assessment_types}"
   due = inp.info.get('due', False)
   if due:
      # If there's a due date, during makeing of the rubric ensure it matches datetime format
      try:
          datetime.strptime(due, '%Y-%m-%d %H:%M:%S')
      except ValueError as e:
          raise BaseException(f'For {key}, the due date of {due} returns {e}') from e
   for who, exception in inp.info.get('exceptions', {}).items():
       for k, v in exception.items():
           if k == 'due':
              # If there's a due date, during makeing of the rubric ensure it matches datetime format
              try:
                  datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
              except ValueError as e:
                  raise BaseException(f'For {key} {k}, the due date of {v} returns {e}') from e

   inp = inputs(key) # reset
   bottle.template(tmd_path, constant_e=math.e, constant_pi=math.pi, log=math.log,
                   get_url=lambda x, **y: x, **inp.env(), **locals(), **dotenv.dotenv_values())
   rubrics, _, _ = inp.save()
   return key, rubrics, inp.info

def updateRubrics(cursor, key, rubrics, info, mtime):
   """Update the db to contain the problems"""
   print(f"updateRubrics: updating rubrics for {key}")
   answers = {tag: rubrics[tag]["solution"] for tag in rubrics}
   answers["_info"] = info
   result = evalMultiple(answers, rubrics)
   # There should be some rubrics if there were any points
   assert result != {} or info.get('points_total', 0) == 0, f"{key}: No results found"

   for tag in result:
      # There should be no errors
      if 'error' in result[tag]:
         if 'tests' in result[tag]:
           for test in result[tag]['tests']:
              if ('context' in test) and ('_aux' in test['context']):
                 print('_aux:')
                 lines = test['context']['_aux'].split('\n')
                 for index, line in enumerate(len(lines)):
                    print(f"{index}: {line}")
         lines = result[tag]['solution'].split('\n')
         for index, line in enumerate(lines):
            if result[tag]['kind'] == 'sql':
               # Print without line number
               print(line)
            else:
               print(f"{index}: {line}")
      assert 'error' not in result[tag] or \
             tag[0] == '_' or \
             result[tag]['points'] == 0, \
             f"{key}: For question {tag} has error {result[tag]['error']}"
   result_json = json.dumps(result, default=json_converter)
   info_json = json.dumps(info, default=json_converter)
   cursor.execute("""
        insert into rubrics (key, time, questions, info, assessment_type)
               values (%(key)s, %(time)s, %(questions)s, %(info)s, %(assessment_type)s)
               on conflict (key) do
               update set questions=%(questions)s, info=%(info)s,
                          time=%(time)s, assessment_type=%(assessment_type)s  """,
                  dict(key=key, time=mtime, questions=result_json,
                       info=info_json, assessment_type=info['assessment_type']))
   cursor.connection.commit()


def main(cursor):
   """Process questions"""
   # process all the content to get answers and codes
   paths = []
   for folder in assessment_folders + ['oldstuff']:
      paths.extend(glob(f"content/{folder}/*.tmd"))
      paths.extend(glob(f"content/{folder}/*.itmd"))
   allCodes = {}
   for path in paths:
      # if args.verbose:
      #   print(f"Processing {path}")
      key, rubrics, info = getRubrics(path, cursor)
      codes = info.get("codes", {})
      mtime = datetime.fromtimestamp(osp.getmtime(path))
      # scream on code conflict
      for code in codes:
         if code in allCodes:
            print(code, path)
            assert code not in allCodes
         allCodes[code] = codes[code]
      # see if we need to update the db
      cursor.execute("""select time from rubrics where key = %s""", [key])
      row = cursor.fetchone()
      if row is None or row.time < mtime or args.force:
         updateRubrics(cursor, key, rubrics, info, mtime)

   # update the codes in the db
   for code in allCodes.items():
      cursor.execute("""insert into codes (time, code)
                      values (%(expires)s, %(code)s)
                      on conflict (code) do
                      update set time=%(expires)s""",
                     {"code": code, "expires": allCodes[code]},
                     )


if __name__ == "__main__":
   db.init()
   conn = db.open_db()
   with contextlib.closing(conn):
       c = conn.cursor()
       main(c)
