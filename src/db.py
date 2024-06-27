"""
database wrapper for COMP550 mypoll code
"""
# pylint: disable=too-many-branches, unsupported-membership-test, too-many-statements, bad-indentation
import contextlib
import getpass
import os
import pwd
import re
import sys

import psycopg2
import psycopg2.extras

import config
from config import (assessment_types, valid_sections )

connection_string = ""

# Note: You must manually `sudo -u postgres createuser <username> for everyone in config.admins
# Note: You just do:  sudo -u postgres psql mypoll
#                     mypoll=# create extension btree_gist;

def log(*args):
   """Print for debugging"""
   print(*args, file=sys.stderr)

def init(host=None):
   """initialize my db setup"""
   global connection_string  # pylint: disable=global-statement

   if os.getcwd().startswith("/var/www/mypoll"):
      connection_string = "dbname='mypoll' user='www-data'"
   else:
      username = getpass.getuser()
      connection_string = f"dbname='mypoll' user='{username}'"
      if host:
         connection_string += f" host='{host}'"
   createTables()  # pylint: disable=no-value-for-parameter


def open_db():
   """Open the database, return the connection"""
   assert connection_string != "", 'You must run db.init() before running db.open_db'
   # If on the test system you get psycopg2.OperationalError: could not connect to server: No such file or directory
   # ln -s  /var/run/postgresql/.s.PGSQL.5432 /tmp/.s.PGSQL.5432
   return psycopg2.connect(
      connection_string, cursor_factory=psycopg2.extras.NamedTupleCursor
   )

# a decorator to manage db access
def with_db_cursor(func):
   """Add an extra argument with a database connection"""

   def func_wrapper(*args, **kwargs):
      connection = open_db()
      with contextlib.closing(connection):
         cursor = connection.cursor()
         result = func(*args, **dict(kwargs, cursor=cursor))
         connection.commit()
         return result

   return func_wrapper


@with_db_cursor
def createTables(cursor):  # pylint: disable=too-many-statements
   """define tables for mypoll"""
   admins = ['www-data']
   for a in config.admins:
       try:
           pwd.getpwnam(a)
           admins.append(a)
       except KeyError:
           continue  # User doesn't exist

   def createTableAndGrants(cursor, table, create, grants):
      """ Test if table exists. If not create and do grants"""
      cursor.execute(f"""
            select exists(
                   select 1 from information_schema.tables
                       where table_catalog = 'mypoll' and
                             table_name='{table}')"""
                )
      row = cursor.fetchall()
      if not row[0].exists:
         log(f'createTableAndGrants: {create}')
         cursor.execute(create)
         for grant in grants:
            try:
               log(f'createTableAndGrants: {grant}')
               cursor.execute(grant)
            except Exception as e:
               log(f'createTables: {grant}: {e}')
               raise

   def createFunction(cursor, name, create):
        """ Test if function exists. If not create a function """
        cursor.execute("""
                SELECT EXISTS(SELECT 1
                                FROM pg_proc
                               WHERE proname=%(name)s)  """,
                       dict(name=name))
        row = cursor.fetchall()
        if not row or not row[0].exists:
           log(f'createFunction: {create}')
           cursor.execute(create)

   def createViewAndGrants(cursor, view, create, grants):
      """ Test if view exists. If not create"""
      cursor.execute("""
            select exists(
                   select 1 from pg_views
                       where schemaname='public' and
                             viewname=%(view)s)""",
                  dict(view=view))
      row = cursor.fetchall()
      if not row or not row[0].exists:
         log(f'createViewAndGrants: {create}')
         cursor.execute(create)
         for grant in grants:
            try:
               log(f'createViewAndGrants: {grant}')
               cursor.execute(grant)
            except Exception as e:
               log(f'createTables: {grant}: {e}')
               raise

   # record their posts
   grants = ([f"""grant all privileges on table post to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table post_post_id_seq to "{userid}" """ for userid in admins])
   createTableAndGrants(cursor, "post", """
        create table if not exists post
        (post_id serial primary key,
         time timestamp,
         onyen text,
         key text,
         ip text)""",
                        grants)
   # Need to do manually as table owner
   # CREATE INDEX post_id_index on post (post_id)


   # active_sections
   grants = ([f"""grant all privileges on table active_sections to "{userid}" """ for userid in admins]+
             [f"""grant all privileges on table active_sections_id_seq to "{userid}" """ for userid in admins])
   createTableAndGrants(cursor, "active_sections", """
            create table if not exists active_sections
            (id serial primary key,
             page_id serial references pages(id) ON DELETE CASCADE,
             page_section text,
             UNIQUE (page_id, page_section))""",
                           grants)

   # record their answers
   grants = ([f"""grant all privileges on table answers to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table answers_answer_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "answers", """
        create table if not exists answers
        (answer_id serial primary key,
         post_id serial references post(post_id) ON DELETE CASCADE,
         field text,
         value text)  """,
                        grants)
   # Need to do manually as table owner
   # CREATE INDEX answer_field ON answers (field)

   # record them fetching questions
   grants = ([f"""grant all privileges on table fetched to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table fetched_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "fetched", """
        create table if not exists fetched
        (id serial primary key,
         time timestamp,
         onyen text,
         key text,
         pages text[] default '{}',
         url text,
         ip text)""",
                        grants)

   # record the 404 response codes (not found)
   grants = ([f"""grant all privileges on table notfound to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table notfound_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "notfound", """
        create table if not exists notfound
        (id serial primary key,
         time timestamp,
         onyen text,
         url text,
         ip text)""",
                        grants)

   # create a table for zoom
   grants = [f"""grant all privileges on table zoom to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "zoom", f"""
        create table if not exists zoom
        (url text,
         lecture_date date,
         section text
            constraint valid_section
            check (section in {tuple(valid_sections)}))
         """,
                        grants)

   # record various state
   grants = ([f"""grant all privileges on table state to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table state_id_seq to "{userid}" """ for userid in admins])
   createTableAndGrants(cursor, "state", """
        create table if not exists state
        (id serial primary key,
         key text unique,
         value text)""",
                        grants)

   # record browser events
   grants = ([f"""grant all privileges on table browser to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table browser_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "browser", """
        create table if not exists browser
        (id serial primary key,
         time timestamp,
         onyen text,
         event text,
         key text)""",
                        grants)

   # record valid submit codes
   grants = ([f"""grant all privileges on table codes to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table codes_id_seq to "{userid}" """ for userid in admins])
   createTableAndGrants(cursor, "codes", """
        create table if not exists codes
        (id serial primary key,
         time timestamp,
         code text unique)""",
                        grants)

   # associate info with posts for reporting scores and such
   grants = ([f"""grant all privileges on table feedback to "{userid}" """
              for userid in admins] +
             [f"""grant all privileges on table feedback_post_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "feedback", """
        create table if not exists Feedback
        (post_id serial primary key references post(post_id) ON DELETE CASCADE,
         score real,
         points_total real,
         elapsed_time interval,
         msg text,
         external_msg text default '' )  """,
                        grants)


   # create a table for rubrics
   grants = [f"""grant all privileges on table rubrics to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "rubrics", f"""
        create table if not exists rubrics
        (key text primary key,
         time timestamp,
         assessment_type text constraint valid_rubric_type
                                   check (assessment_type in {tuple(assessment_types)}),
         questions json not NULL,
         info json not NULL)""",
                        grants)

   # create the roll table
   grants = [f"""grant all privileges on table roll to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "roll", f"""
        create table if not exists roll
        (onyen text primary key,
         pid text,
         name text,
         password text,
         section text
            constraint valid_section
            check (section in {tuple(valid_sections)}),
         email text default NULL,
         imageURL text,
         zwsp text,
         rid serial unique,
         graduate_student boolean default false,
         conflict_exam boolean default false,
         team_member_number integer DEFAULT 0,
         team_number integer DEFAULT 0,
         game_alias_name text UNIQUE default NULL,
         exam_seat text default '',
         exam_url text default '',
         exam_time timestamp default '2022-12-01 16:00:00',
         extended real default 0)""",
                        grants)

   # assessment_percentages
   grants = [f"""grant all privileges on table assessment_percentages to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "assessment_percentages", """
            create table if not exists assessment_percentages
            (onyen text references roll(onyen)
                   ON DELETE CASCADE, -- override a student's weights using onyen
             worksheets float default 5,
             homeworks float default 15,
             games float default 6,
             fe float default 30,
             midterm1 float default 22.5,
             midterm2 float default 22.5,
             UNIQUE (onyen)
             )""",
                        grants)

   # After grading create an assessment grade
   grants = [f"""grant all privileges on table assessments to "{userid}" """ for userid in admins]
   # Create a string that represents all the assessment types
   # Handle the case of a suple of just one thing by removing the comma 
   assessment_types_str =  re.sub("',\)", "')", str(tuple(config.assessment_types)))
   createTableAndGrants(cursor, "assessments", f"""
        create table if not exists assessments
          (key text references rubrics(key) ON DELETE CASCADE,
           assessment_type text constraint valid_rubric_type
                                   check (assessment_type in {assessment_types_str}),
           onyen text references roll(onyen) ON DELETE CASCADE,
           overall_percentage real,  -- Weighted score percentage
           one_submission_graded_100_percent bool default False,
           number_submissions integer,
           number_graded integer,
           PRIMARY KEY(key, onyen),
           UNIQUE(key, onyen, assessment_type),
           CONSTRAINT assessment_submissions_non_negative CHECK (number_submissions>=0),
           CONSTRAINT assessment_graded_non_negative CHECK (number_graded >=0)) """,
           grants)

   # create a classroll table
   grants = ([f"""grant all privileges on table zwsp to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table zwsp_id_seq to "{userid}" """ for userid in admins])
   createTableAndGrants(cursor, "zwsp", """
        create table if not exists zwsp
        (id        serial primary key,
         post_id integer references post(post_id) ON DELETE SET NULL,
         fieldname text,
         s_onyen   text )""",
                        grants)

   grants = [f"""grant all privileges on table grades to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "grades", """
        create table if not exists grades
        (onyen           text primary key references roll(onyen) ON DELETE CASCADE,
         letterGrade     text,
         total           float default 0,
         fe              float default 0,
         midterm2        float default 0,
         midterm1        float default 0,
         homeworks       float default 0,
         games           float default 0,
         worksheets      float default 0)  """,
                        grants)

   grants = ([f"""grant all privileges on table worksheet_bonus to "{userid}" """
              for userid in admins] +
             [f"""grant all privileges on table worksheet_bonus_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "worksheet_bonus", """
        create table if not exists worksheet_bonus
        (id              serial primary key,
         onyen           text,
         submitter       text,
         share_time      timestamp,
         reason          text,
         ip              text,
         points          float default 50)""",
                        grants)

   grants = ([f"""grant all privileges on table game_bonus to "{userid}" """
              for userid in admins] +
             [f"""grant all privileges on table game_bonus_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "game_bonus", """
        create table if not exists game_bonus
        (id              serial primary key,
         onyen           text,
         reason          text,
         key             text,
         explanation     text,
         points          float default 50)""",
                        grants)


   # create a table for agenda checklists
   grants = ([f"""grant all privileges on table checklist to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table checklist_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "checklist", """
        create table if not exists checklist
        (id serial primary key,
         lecture_date date,
         item text,
         time timestamp,
         checked boolean default false,
         onyen text references roll(onyen) ON DELETE CASCADE)""",
                        grants)

   # create a table for agenda checklists
   grants = [f"""grant all privileges on table checklist_worksheet to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "checklist_worksheet", """
        create table if not exists checklist_worksheet
        (lecture_date date,
         item text,
         key text references rubrics(key) ON DELETE CASCADE,
         UNIQUE (lecture_date, item, key))  """,
                        grants)

   # record them submitting notebooks
   grants = ([f"""grant all privileges on table notebooks to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table notebooks_notebook_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "notebooks", """
        create table if not exists notebooks
        (notebook_id serial primary key,
         time timestamp,
         onyen text,
         key text,
         filename TEXT NOT NULL,
         modified TIMESTAMP DEFAULT '2023-01-01 00:00:00',
         saved TIMESTAMP DEFAULT '2023-01-01 00:00:00',
         voided boolean default false,
         ip text )""",
         grants)

   # Corrections table
   grants = [f"""grant all privileges on table corrections to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "corrections", """
        create table if not exists corrections
        (id serial primary key,
         onyen text, -- This is not yet filled in, darn
         key text not null,
         post_id integer references post(post_id) ON DELETE CASCADE,
         field text not null,
         score float,
         remarks text default '')  """,
         grants)


   # record the graded notebooks
   grants = [f"""grant all privileges on table graded_notebooks to "{userid}" """ for userid in admins]
   createTableAndGrants(cursor, "graded_notebooks", """
        create table if not exists graded_notebooks
        (url text primary key,
         time timestamp,
         notebook_id SERIAL REFERENCES Notebooks(notebook_id) ON DELETE CASCADE,
         hourslate integer default 0,
         hoursearly integer default 0,
         missed integer default 0,
         partial_credit float default 0,
         avgDistance float default 0,
         penalty_score FLOAT,         -- Amount to decrease due to hours late
         bonus_score FLOAT,           -- Amount to increase due to hours early
         score float,
         score_total float,           -- score minus penalty plus bonus
         points_total float)   """,
         grants)

   # record notebook statistics
   grants = ([f"""grant all privileges on table notebook_statistics to "{userid}" """ for userid in admins] +
             [f"""grant all privileges on table notebook_statistics_id_seq to "{userid}" """
              for userid in admins])
   createTableAndGrants(cursor, "notebook_statistics", """
        CREATE TABLE IF NOT EXISTS Notebook_statistics
        (id SERIAL PRIMARY KEY,
         key TEXT NOT NULL,
         onyen TEXT NOT NULL,
         time TIMESTAMP,
         name TEXT NOT NULL,
         status TEXT,
         UNIQUE (key, onyen, time))  """,
                        grants)

   # create a view of the worksheets
   grants = ([f"""grant all privileges on table worksheets to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'worksheets', """
         CREATE VIEW worksheets (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='worksheet' and
                      P.id=A.page_id  """, grants)

   # create a view of the games
   grants = ([f"""grant all privileges on table games to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'games', """
         CREATE VIEW games (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='games' and
                      P.id=A.page_id  """, grants)

   # create a view of the homeworks
   grants = ([f"""grant all privileges on table homeworks to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'homeworks', """
         CREATE VIEW homeworks (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='homework' and
                      P.id=A.page_id  """, grants)

   # create a view of the midterm1
   grants = ([f"""grant all privileges on table midterm1 to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'midterm1', """
         CREATE VIEW midterm1 (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='midterm1' and
                      P.id=A.page_id  """, grants)

   # create a view of the midterm2
   grants = ([f"""grant all privileges on table midterm2 to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'midterm2', """
         CREATE VIEW midterm2 (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='midterm2' and
                      P.id=A.page_id  """, grants)

   # create a view of the fe
   grants = ([f"""grant all privileges on table fe to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'fe', """
         CREATE VIEW fe (key, onyen, section) AS
              SELECT DISTINCT P.key, onyen, section
                FROM pages P, active_sections A, rubrics R
                WHERE P.key=R.key and
                      R.assessment_type='fe' and
                      P.id=A.page_id  """, grants)


   # create a view of the submitted
   grants = ([f"""grant all privileges on table all_submitted to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'all_submitted', """
         CREATE VIEW all_submitted (post_id, key, onyen) AS
              SELECT P.post_id as post_id, key, onyen
                FROM Post P, Answers A
                WHERE P.post_id=A.post_id AND
                      A.field='_submit' AND
                      A.value='Submit'

              UNION

              SELECT notebook_id, key, onyen
                FROM Notebooks
               WHERE voided=false  """,
                       grants)

   # create a view of the submitted
   # grants = ([f"""grant all privileges on table submitted_deprecated to "{userid}" """ for userid in admins])
   # createViewAndGrants(cursor, 'submitted_deprecated', """
   #       CREATE VIEW submitted_deprecated (post_id, key, onyen) AS
   #            SELECT min(P.post_id) as post_id, key, onyen
   #              FROM Post P, Answers A
   #              WHERE P.post_id=A.post_id AND
   #                    A.field='_submit' AND
   #                    A.value='Submit'
   #              GROUP by key, onyen
   #
   #            UNION
   #
   #            SELECT min(notebook_id) as id, key, onyen
   #              FROM Notebooks
   #             WHERE voided=false
   #              GROUP BY key, onyen  """, grants)

   # create a view of the graded assessments
   grants = ([f"""grant all privileges on table graded to "{userid}" """ for userid in admins])
   createViewAndGrants(cursor, 'graded', """
         CREATE VIEW graded (id, key, onyen) AS
              SELECT P.post_id, P.key, P.onyen
                FROM Post AS P, Feedback as F
               WHERE P.post_id=F.post_id

              UNION

              SELECT G.notebook_id, N.key, N.onyen
                FROM Graded_notebooks as G, Notebooks as N
               WHERE G.notebook_id = N.notebook_id   """, grants)

   createFunction(cursor, 'answers_exist_for_user_and_key', """
           CREATE OR REPLACE FUNCTION Answers_exist_for_user_and_key(onyen_parm text, key_parm text)
              RETURNS boolean
              LANGUAGE sql AS $func$
                    -- Return true if this assessment currently has an active page of 'answer'
                    WITH Ids AS (SELECT P.id, RANK() OVER(Partition BY P.key       -- rank within each key
                                                          Order BY P.onyen DESC)  -- prefer onyen pages
                                                          AS rank_num
                                         FROM Pages AS P, Roll R
                                        WHERE R.onyen=onyen_parm AND
                                              P.key = key_parm AND
                                              (P.onyen=R.onyen OR (P.onyen='' and P.section=R.section)) AND
                                              P.start_time <= now() AND
                                              P.end_time >= now())

                    SELECT EXISTS(SELECT 1
                                  FROM IDS, Active_sections, Assessments A
                                 WHERE IDS.id = Active_sections.page_id AND
                                       A.key=key_parm AND
                                       A.onyen=onyen_parm AND
                                       A.one_submission_graded_100_percent AND
                                       LOWER(Active_sections.page_section) = 'answers')
                        $func$   """)

   createFunction(cursor, 'all_assessments', """
           CREATE OR REPLACE FUNCTION All_assessments(onyen_parm text)
                RETURNS table (assessment_type TEXT, key TEXT) AS
                  $body$
                      -- Return true if this assessment currently has an active page of 'answer'
                      WITH Ids AS (SELECT P.id, RANK() OVER(Partition BY P.key       -- rank within each key
                                                            Order BY P.onyen DESC)  -- prefer onyen pages
                                                            AS rank_num
                                           FROM Pages AS P, Roll R
                                          WHERE R.onyen=onyen_parm AND
                                                (P.onyen=R.onyen OR (P.onyen='' and P.section=R.section)) AND
                                                P.start_time <= now() AND
                                                P.end_time >= now())

                      SELECT R.assessment_type, R.key
                        FROM Rubrics R, Ids I, Pages P
                       WHERE P.key = R.key AND
                             P.id = I.id AND
                             I.rank_num = 1
                  $body$
                  language sql    """)
