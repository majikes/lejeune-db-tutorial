#!/usr/bin/python3
"""
COMP 550 administration endpoints
"""

# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation
from collections import namedtuple
import glob
import os.path as osp

from appbase import (StripPathMiddleware,  # pylint: disable=unused-import
                     allow_json, app, application, auth, get_url, get_onyen,
                     renderMarkdown, renderTemplate, serve, onyen_is_admin,
                     onyen_is_john, onyen_is_known)
from apputilities import (generate_submit_code, get_text, get_worksheet_bonus_information,
                          log, not_allowed, not_found, set_worksheet_bonus)
from assessments import SUBMITTABLE_PAGES
from bottle import request, view
from config import assessment_folders, valid_sections
from db import with_db_cursor



@app.get("/ungraded", name="ungraded")
@auth(onyen_is_admin)
@with_db_cursor
@view("ungraded")
def ungraded(cursor):
   """List all assessments that are ungraded"""

   # Get all post_id's that have not been graded
   cursor.execute("""
       SELECT S.post_id, S.key, S.onyen
         FROM All_Submitted AS S
        WHERE (S.key, S.onyen) NOT IN (SELECT G.key, G.onyen
                                         FROM Graded as G)
        ORDER BY S.Key, S.onyen, S.post_id  """)

   return {'ungraded': cursor.fetchall()}


@app.get("/welcome", name="welcome")
@auth(onyen_is_admin)
@with_db_cursor
@view("welcome")
def welcome(cursor):
   """Show the results of the welcome worksheet """
   if request.query.section:
      sections = [request.query.section]
   else:
      sections = valid_sections

   welcome_answers = {}
   for k, v in dict(Concerns='Concern%%',
                    John='John%%',
                    Thoughts='Thought%%',
                    About='You%%').items():
      cursor.execute("""
        SELECT DISTINCT LOWER(A.value) as value
          FROM Answers AS A, Post AS P, Roll as R
         WHERE A.post_id = P.post_id AND
               R.onyen = P.onyen AND
               A.field like %(question_type)s AND
               R.section in %(sections)s AND
               P.key='worksheet-00-welcome' AND
               LOWER(A.value) not like '%%no %%concern%%' AND
               LOWER(A.value) not like '%%i have not thought%%' AND
               LOWER(A.value) not like '%%nothing %%to %%share%%' AND
               LOWER(A.value) not like '%%i %%any questions%%' AND
               LOWER(A.value) not like '%%no %%question%%'
         ORDER BY LOWER(A.value)   """,
                     dict(sections=tuple(sections),
                          question_type=v))
      welcome_answers[k] = cursor.fetchall()

   return dict(answers=welcome_answers)


@app.get("/submittable", name="submittable")
@auth(onyen_is_john)
@with_db_cursor
@view("submittable")
def submittables(cursor):
   """List all assessments that students can submit """
   cursor.execute("""
        SELECT P.key, P.section, P.onyen, ARRAY_AGG(A.page_section) as page_sections
          FROM pages AS P, active_sections AS A
         WHERE A.page_section in %(submittable_pages)s AND
               P.id=A.page_id AND
               P.start_time < now() AND -- page access start time has occurred
               P.end_time >= now() AND  -- page access end time has not occurred
               P.section != '003' AND
               P.onyen NOT LIKE 'student%%'
         GROUP BY P.key, P.section, P.onyen
         ORDER BY P.key, P.section, P.onyen, page_sections  """,
                  dict(submittable_pages=tuple(SUBMITTABLE_PAGES)))

   return {"assessments": cursor.fetchall()}


@app.get("/visualizations", name="visualizations")
@auth(onyen_is_admin)
@view("visualizations")
def visualizations():
   """List all assessments with most recent first"""
   # This hack of reusing the request.url does not work on localhost
   files = glob.glob("./visualization/*.html")
   all_visualizations = [{"name": osp.splitext(osp.basename(f))[0],
                          "url": f"{request.url[:-1]}/{osp.basename(f)}"}
                         for f in files
                         if osp.basename(f) != 'index.html']
   all_visualizations.append({"name": "joins",
                              "url": "/visualization/joins.html"})
   return dict(visualizations=all_visualizations)


@app.get("/assessments", name="assessments")
@auth(onyen_is_john)
@view("assessments")
def assessments():
   """List all assessments with most recent first"""
   all_assessments = {}
   for folder in assessment_folders:
      files = glob.glob(f"content/{folder}/*.tmd")
      if len(files) > 0:
         files.sort()
         all_assessments[folder] = [{"key": osp.splitext(osp.basename(f))[0],
                                     "text": get_text(f)} for f in files]
      else:
         all_assessments[folder] = None

   return {"assessments": all_assessments}


@app.get("/responses/<key>/<onyen>")
@auth(onyen_is_admin)
@view("student_answers")
@with_db_cursor
def get_student_answers(key, onyen, cursor):
   """ return info on a student's answers """
   cursor.execute("""
        SELECT P.time, A.field, A.value
          FROM Answers AS A, Post AS P
         WHERE A.post_id = P.post_id AND
               P.onyen = %(onyen)s AND
               P.key = %(key)s
            order by time, field  """,
                  dict(onyen=onyen, key=key))
   return {"answers": cursor.fetchall, "key": key, "onyen": onyen}


@app.get("/responses/<key>")
@auth(onyen_is_admin)
@view("answers")
@with_db_cursor
def get_answers(key, cursor):
   """ return info on the answers """
   cursor.execute("""
       WITH Ids AS (SELECT MAX(P.post_id) AS post_id
                      FROM Post AS P
                     WHERE P.key = %(key)s
                     GROUP BY P.onyen)

       SELECT A.field, A.value, COUNT(A.value) AS count
         FROM Answers AS A, Ids AS I
        WHERE A.post_id = I.post_id
        GROUP BY A.field, A.value
        ORDER BY A.field, count DESC  """,
                  dict(key=key))
   return {"answers": cursor.fetchall(), "key": key}


@app.get("/submitcode", name="submitcode")
@auth(onyen_is_admin)
@with_db_cursor
@view("displaySubmitCode")
@allow_json
def newSubmitCode(cursor):
   """Generate and return a new submit code"""
   new_code, now = generate_submit_code(cursor)
   url = request.query.get("url")
   if url:
      p = request.urlparts
      url = f'{p.scheme}://{p.hostname}{app.get_url("root")}{url}'

   return {"code": new_code, "url": url, "time": now.strftime("%H:%M")}


@app.get("/mathjax", name="mathjax")
@auth(onyen_is_admin)
@view("mathjax")
@allow_json
def mathjax():
   """Generate a Latex data entry screen"""
   return


@app.get("/notes", name="notes")
@auth(onyen_is_admin)
@view("notes")
@allow_json
def notes():
   """Generate a notes data entry screen"""
   return

@app.get("/roll", name="roll")
@auth(onyen_is_admin)
@with_db_cursor
@view("roll")
def get_roll(cursor):
   """Present class roll with links"""
   section = request.query.get('section', '')
   cursor.execute("""
       SELECT R.onyen, R.pid, R.name
         FROM Roll AS R
        WHERE R.onyen NOT LIKE 'student%'
    """)
   roll = cursor.fetchall()
   if section:
      roll = [item for item in roll if item.section == section]
   return {"roll": roll, "section": section}



@app.get("/videos", name="videos")
@auth(onyen_is_admin)
@view("videos")
def videos():
   """List all Videos with most recent first"""
   files = glob.glob("/var/www/videos/*.mp4")
   if len(files) > 0:
      files.sort()
      all_videos = [{"name": osp.basename(f)[:-4],
                     "url": get_url("video", video=osp.basename(f)[:-4])} for f in files]
   else:
      all_videos = []

   return {"videos": all_videos}


# Show a student bonus panel
@app.route("/worksheet_bonus", name="worksheet_bonus", method="GET")
@auth(onyen_is_admin)
@with_db_cursor
@view("worksheet_bonus")
def worksheet_bonus(cursor):
   """ Record bonus points for class participation """
   section = request.query.get('section', '')

   return get_worksheet_bonus_information(cursor, section)

@app.post("/worksheet_bonus", name="worksheet_bonus_submit", method="POST")
@auth(onyen_is_admin)
@with_db_cursor
@view("worksheet_bonus")
@allow_json
def worksheet_bonus_submit(cursor):
   """ Accept a worksheet bonus submission from LA, TA or me """
   form = request.forms.decode('utf-8')
   onyen = form["onyen"]
   submitter = get_onyen()
   reason = form["reason"]
   section = form.get("section", "")
   ip = request.remote_addr

   if (not reason) or (not onyen):
      log(f"worksheet_bonus reason/onyen cannot be null. reason={reason}, onyen={onyen}")
      not_found(cursor)
   return set_worksheet_bonus(cursor, onyen, submitter, reason, ip, section)


@app.get("/stats", name="stats")
@auth(onyen_is_admin)
@with_db_cursor
@view("stats")
def get_stats(cursor):
   """Present a summary statistics page"""
   cursor.execute("""
        WITH S_score  AS (SELECT S.key, S.onyen, score * 100.0 / points_total AS score
                            FROM All_Submitted AS S, Roll AS R, Rubrics, Feedback F
                           WHERE S.onyen = R.onyen AND
                                 S.post_id = F.post_id AND
                                 S.key = Rubrics.key AND
                                 R.section in ('001', '002') AND
                                 R.onyen not like 'student%'),
             S_counts AS (SELECT key, count(distinct onyen) as submitted_count, AVG(score) AS average,
                                    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY score ASC) AS median
                            FROM S_score
                           GROUP BY key),
             F_counts AS (SELECT F.key, count(distinct F.onyen) as fetched_count, Rubrics.assessment_type
                            FROM Fetched AS F, Roll AS R, Rubrics
                           WHERE F.onyen = R.onyen AND
                                 F.key = Rubrics.key AND
                                 R.section in ('001', '002') AND
                                 R.onyen not like 'student%'
                           GROUP BY F.key, Rubrics.assessment_type)

        SELECT F.key, F.assessment_type, F.fetched_count, COALESCE(S.submitted_count, 0) AS submitted_count,
                 S.average, S.median
          FROM F_counts AS F
          JOIN S_counts AS S ON F.key = S.key
         ORDER BY F.assessment_type, F.key  """)
   these_assessments = cursor.fetchall()

   cursor.execute("""
        SELECT AVG(midterm1) as m1_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY midterm1 ASC) as m1_median,
               AVG(midterm2) as m2_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY midterm2 ASC) as m2_median,
               AVG(midterm2+m2_partial_credit) as m2_with_partial_credit_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY midterm2+m2_partial_credit ASC) as m2_with_partial_credit_median,
               AVG(fe) AS fe_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY fe ASC) as fe_median,
               AVG(worksheets) AS worksheet_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY worksheets ASC) as worksheet_median,
               AVG(games) AS game_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY games ASC) as game_median,
               AVG(homeworks) AS homework_average,
                 PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY homeworks ASC) as homework_median
          FROM Grades AS G, Roll AS R
         WHERE G.onyen = R.onyen AND
               R.section in ('001', '002') AND
               R.onyen not like 'student%'
                  """)
   these_grades = cursor.fetchone()

   return dict(assessments=these_assessments,
               grades=these_grades)

@app.get("/stats-games", name="stats_games")
@auth(onyen_is_admin)
@with_db_cursor
@view("stats-games")
def get_stats_games(cursor):
   """Present a summary game qualitative data """
   questions = {'Green.Highlights': 'I find/found the correct-answer, green-highlight of the Chrome-based system helpful',
                'Game.Worry': 'A am worried / no longer worry about the database game',
                'Pregame': 'I think the games will be / was helpful in preparing for the exam',
                'Ready.Game': 'I feel / felt ready to play the database game',
                'Game.Interest': 'I think that gamificaiton will improve / increased my interest in databases',
                'Database.Understanding': 'I think the gamificaiton will improve / improved my understanding of databases',
                'Database.Enjoyment': 'I think will increase / increased my enjoyment of databases',
                'More.Games': 'I look forward to more gamification in education',
                'Do.Well': 'I believe I will do well / did well in the database game'}
   likert_scale = {'1': 'Strongly disagree',
                   '2': 'Disagree',
                   '3': 'Neutral',
                   '4': 'Agree',
                   '5': 'Strongly agree',
                   '6': 'Prefer not to answer'}

   cursor.execute("""
        SELECT S.key, field as question, value, count(*)
          FROM All_Submitted S, Answers A
         WHERE S.post_id=A.post_id AND
               S.key in ('worksheet-game-nuclear-01', 'worksheet-game-nuclear-02') AND
               substr(A.field, 1, 1) != '_' AND
               A.field != 'Feelings'
         GROUP BY field, value, S.key
                  """)
   likerts = cursor.fetchall()
   keys = sorted(set(l.key for l in likerts))
   assert len(keys) == 2, 'This assumes there are two keys: the alph-first being pre, and the alpha-last being post'
   likert_values = [f'{x}' for x in range(int(min(likert_scale.keys())), int(max(likert_scale.keys()))+1)]

   # change from a record to a dictionary
   pre_post_likerts = {}
   for l in likerts:
       if l.key not in pre_post_likerts:
           pre_post_likerts[l.key] = {}
       if l.question not in pre_post_likerts[l.key]:
           pre_post_likerts[l.key][l.question] = {}
       pre_post_likerts[l.key][l.question][l.value] = l.count

   # Ensure all values present and make percentage
   for key in keys:
       for question in questions:
           total = sum(pre_post_likerts[key][question].values())
           for value in likert_values:
               pre_post_likerts[key][question][value] = round(pre_post_likerts[key][question].get(value, 0) * 100 / total, 1)

   # Get the feelings before and after the game
   cursor.execute("""
        SELECT S.key, lower(value) AS text, count(*) AS count
          FROM All_Submitted S, Answers A
         WHERE S.post_id=A.post_id AND
               S.key in ('worksheet-game-nuclear-01', 'worksheet-game-nuclear-02') AND
               LENGTH(A.value) > 1 AND
               A.field = 'Feelings'
         GROUP BY S.key, lower(value)
         ORDER BY S.key, lower(value)
                  """)
   feeling_comments = cursor.fetchall()
   F = namedtuple('F', 'text count')
   feelings = {key: [] for key in keys}
   for f in feeling_comments:
       feelings[f.key].append(F(text=f.text.strip(), count=f.count))

   return dict(pre_post_likerts=pre_post_likerts,
               likert_scale=likert_scale,
               keys=keys,
               questions=questions,
               feelings=feelings)


@app.post("/unsubmit", name="unsubmit")
@auth(onyen_is_admin)
@with_db_cursor
def unsubmit(cursor):
   """ Unsubmit a submission """
   if not onyen_is_john(get_onyen()):
      not_allowed()
   key = request.forms.decode('utf-8').key
   onyen = request.forms.decode('utf-8').onyen
   post_id = request.forms.decode('utf-8').post_id
   cursor.execute("""
        SELECT 1
          FROM Answers AS A, Post AS P
         WHERE A.post_id = P.post_id AND
               A.field='_submit' AND
               A.value like '%%Submit%%' AND
               P.key = %(key)s AND
               P.post_id = %(post_id)s AND
               P.onyen = %(onyen)s  """,
                  dict(onyen=onyen, key=key, post_id=post_id))
   row = cursor.fetchone()
   if not row:
      not_found(cursor)
   cursor.execute("""
       UPDATE Answers SET value = 'unsubmitted'
          WHERE value='Submit' AND
                field='_submit' AND
                post_id=%(post_id)s """,
                  dict(post_id=post_id))

   cursor.execute("""
       DELETE FROM Feedback
             WHERE post_id in (SELECT P.post_id
                                 FROM Post AS P
                                WHERE P.key=%(key)s AND
                                      P.onyen=%(onyen)s)   """,
                  dict(key=key,
                       onyen=onyen))

   cursor.execute("""
       UPDATE Assessments set number_graded = 0,
                              number_submissions = number_submissions-1,
                              overall_percentage = 0
                    WHERE key=%(key)s AND
                          onyen=%(onyen)s  """,
                  dict(key=key,
                       onyen=onyen))

   return {}
