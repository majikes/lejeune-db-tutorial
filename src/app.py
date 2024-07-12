"""
 COMP 421 Specific routes
"""
# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation
import glob
import os.path as osp
from datetime import datetime

import bottle
from appbase import application, StripPathMiddleware  # pylint: disable=unused-import
from appbase import (allow_json, app, auth, get_url, get_onyen, renderMarkdown,
                     get_onyen_for_endpoint,
                     renderTemplate, serve, onyen_is_admin,
                     onyen_is_known)
from apputilities import (checkZWSP, get_team,
                          linkable_header,
                          log, not_allowed, not_found,
                          onyen_in_roll, validateSubmitCode)
from assessments import (get_active_pages,
                         get_assessment_percentages,
                         max_submissions,
                         submit_code_in_pages, submit_in_pages, first_submit_in_pages)
from bottle import redirect, request, static_file, view
from config import assessment_folders
from db import with_db_cursor, init
from editRubrics import editRubrics
from inputs import inputs

# Allow for larger requests
bottle.BaseRequest.MEMFILE_MAX = 1024 * 4096
# Add class directory to template directory
bottle.TEMPLATE_PATH.append('./md-includes/')
bottle.TEMPLATE_PATH.insert(0, './views/')
bottle.TEMPLATE_PATH = list(dict.fromkeys(bottle.TEMPLATE_PATH))
bottle.SimpleTemplate.defaults["get_team"] = get_team
bottle.SimpleTemplate.defaults["linkable_header"] = linkable_header

# Get access to Postgres by calling db.init() to set up the connection string
init()


@app.get(r"/panopto/<hexcode:re:[0-9aA-fF\-]+>", name="panopto")
@auth(onyen_is_known)
@with_db_cursor
@view("assessment.base")
def panopto(cursor, hexcode):
    """Redirect to a unc panopto """
    onyen, _ = get_onyen_for_endpoint()

    now = datetime.now()
    ip = request.remote_addr
    url = f"https://uncch.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id={hexcode}"

    cursor.execute("""
      INSERT INTO Fetched (time, onyen, key, ip, url)
                   VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                   dict(time=now, onyen=onyen, key=url, ip=ip, url=request.url))
    cursor.connection.commit()

    redirect(url)


@app.route("/handouts/<pdf>", name="handouts")
@auth(onyen_is_known)
@with_db_cursor
def pdf_handout(pdf, cursor):
    """ Display a navigation page """

    path = f"content/handouts/{pdf}.pdf"
    if not osp.exists(path):
        log(f"/handout/{pdf} {path} not found")
        not_found(cursor)

    onyen = get_onyen()
    now = datetime.now()
    ip = request.remote_addr
    cursor.execute("""
      INSERT INTO Fetched (time, onyen, key, ip, url)
                   VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                   dict(time=now, onyen=onyen, key=path, ip=ip, url=request.url))
    return static_file(path, root='.')



@app.get("/zoom", name="zoom")
@auth(onyen_is_known)
@with_db_cursor
def zoom(cursor):
   """Redirect to a zoom video"""
   onyen, _ = get_onyen_for_endpoint()

   cursor.execute('''
           SELECT Z.url
             FROM Zoom as Z, Roll R
            WHERE Z.lecture_date = CURRENT_DATE AND
                  Z.section = R.section AND
                  R.onyen = %(onyen)s  ''',
                  dict(onyen=onyen))
   row = cursor.fetchone()
   if row is None:
      msg = f"Zoom lecture for onyen {onyen} for {datetime.today().date()} not found"
      log(f'zoom: {msg}')
      not_found(cursor, msg)
   url = row.url

   now = datetime.now()
   ip = request.remote_addr
   cursor.execute("""
       INSERT INTO Fetched
         (time, onyen, key, ip, url)
         values (%(time)s, %(onyen)s, 'zoom', %(ip)s, %(url)s)
       """,
                  dict(time=now, onyen=onyen, ip=ip, url=request.url))
   cursor.connection.commit()

   redirect(url)

@app.route("/syllabi/<page_name>", name="syllabi")
@with_db_cursor
@auth(onyen_is_known)
@view("syllabi")
def syllabi(page_name, cursor):
   """Render a page such as the syllabus, help, etc."""
   onyen, original_onyen = get_onyen_for_endpoint()
   if not onyen_in_roll(cursor, onyen):
      log(f"syllabi: {onyen} not enrolled in COMP421.")

   path = f"content/syllabi/{page_name}.tmd"
   if not osp.exists(path):
      not_found(cursor)

   title = ""
   with open(path, "rt", encoding='utf-8') as fp:
      top = fp.readline()
      if top.startswith("# "):
         title = title + top[2:].strip()

   # Get whether this onyen has a conflict exam
   cursor.execute("""
                  SELECT R.conflict_exam, R.exam_url, R.exam_time, R.extended
                    FROM Roll AS R
                   WHERE R.onyen=%(onyen)s """,
                  dict(onyen=onyen))
   row = cursor.fetchone()
   conflict_exam = row is not None and row.conflict_exam
   exam_url = row.exam_url if row is not None else 'https://unc.zoom.us/j/99129501388?pwd=bWswaDV6MFBRdUplOWFyaXhteE5qUT09'
   exam_time = row.exam_time if row is not None else datetime(2021, 5, 13, 16, 0)
   extended = row is not None and (row.extended > 0)

   content = renderTemplate(path, onyen=onyen, title=title, conflict_exam=conflict_exam,
                            percentage=get_assessment_percentages(cursor, None),
                            exam_url=exam_url, exam_time=exam_time, extended=extended)
   content = renderMarkdown(content)
   if original_onyen == '':
      cursor.execute("""
        INSERT INTO Fetched (time, onyen, key, ip, pages, url)
                     VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(pages)s, %(url)s)  """,
                     dict(time=datetime.now(), onyen=onyen, key=page_name,
                          ip=request.remote_addr, pages=[], url=request.url))
   return {"base": content, "title": title, "onyen": onyen, "admin": onyen_is_admin(onyen)}


@app.route("/", name="root")
@auth(onyen_is_known)
def home():
   """ Display home page """
   return syllabi("home")  # pylint: disable=no-value-for-parameter


# Process tmd files that do not count toward grades
@app.get("/oldstuff/<key>", name="oldstuff")
@auth(onyen_is_known)
@with_db_cursor
def old_stuff(key, cursor):  # pylint: disable=too-many-statements,too-many-branches
   """
   Allow rendering a set of questions from a template stored in
   the questions folder.
   """
   # renderTemplate uses local so ignore possibly unused variables
   # pylint: disable=possibly-unused-variable
   onyen, _ = get_onyen_for_endpoint()

   path = f"content{request.path}.tmd"
   now = datetime.now()
   if not osp.exists(path):
      log(f"mypoll{request.path}: onyen {onyen} path {path} not found")
      not_found(cursor)
   ip = request.remote_addr
   inp = inputs(key)

   cursor.execute("""
        SELECT R.extended, R.section, R.rid, R.zwsp, R.conflict_exam,
               R.exam_time
          FROM Roll as R
         WHERE R.onyen = %(onyen)s  """,
                  dict(onyen=onyen))
   user_info = cursor.fetchone()
   section = user_info.section
   zwsp = user_info.zwsp
   viewAnswers = user_info.section == '003'

   # get the answers as a json formatted string
   cursor.execute("""
        SELECT R.info, R.questions
          FROM Rubrics AS R
         WHERE R.key = %(key)s   """,
                  dict(key=key))
   rubrics = cursor.fetchone()
   if rubrics is None:
      info = {}
      rubrics = {}
      log(f"old_stuff: no rubrics {key}")
   else:
      info = rubrics.info
      rubrics = editRubrics(rubrics.questions)
   pages = ['questions']

   base = renderTemplate(path, **inp.env(), **locals())
   if base.startswith("\n<pre>"):
      # renderTemplate raised an exception
      return base
   base = renderMarkdown(base)

   # Collect up info variables for psform
   exam = False
   autosave = False
   register_focus_events = False
   pages = []
   result = renderTemplate("psform", **locals())
   if user_info.section != '003':
      cursor.execute("""
       INSERT INTO Fetched (time, onyen, key, ip, pages, url)
                    VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(pages)s, %(url)s)  """,
                     dict(time=now, onyen=onyen, key=key, ip=ip,
                          pages=pages, url=request.url))
   return result


# Process tmd files from assessment_folders
@app.get("/exams/<key>", name="exams")
@app.get("/worksheets/<key>", name="worksheets")
@app.get("/extracredit/<key>", name="extracredit")
@auth(onyen_is_known)
@with_db_cursor
def get_questions(key, cursor):  # pylint:  disable=too-many-statements, too-many-branches
   """
   Allow rendering a set of questions from a template stored in
   the questions folder.
   """
   # Since RendterTemplate uses locals(), ignore possibly unused variables
   # pylint: disable=possibly-unused-variable
   onyen, original_onyen = get_onyen_for_endpoint()
   if not onyen_in_roll(cursor, onyen):
      if key == 'worksheet-demo':
         log(f"{onyen} not enrolled in COMP421. Using worksheet-demo as guest.")
      else:
         not_allowed()

   path = f"content/{request.path}.tmd"
   now = datetime.now()
   if not osp.exists(path):
      log(f"mypoll{request.path}: onyen {onyen} path {path} not found")
      not_found(cursor)
   if key.startswith("_"):  # draft
      if not onyen_is_admin(onyen):
         log(f"mypoll/{request.path} not admin")
         not_found(cursor)
   ip = request.remote_addr

   inp = inputs(key)

   cursor.execute("""
        SELECT R.extended, R.section, R.rid, R.zwsp, R.conflict_exam, R.pid
          FROM Roll AS R
         WHERE R.onyen = %(onyen)s  """,
                  dict(onyen=onyen))
   row = cursor.fetchone()
   section = row and row.section
   extended = row and row.extended
   zwsp = row and row.zwsp
   rid = row and row.rid
   conflict_exam = row and row.conflict_exam
   viewAnswers = section == '003'

   try:
       question_pool_number = int(row.pid) % 2
   except TypeError:
       question_pool_number = 0

   # get the answers as a json formatted string
   cursor.execute("""
        SELECT R.info, R.questions, R.assessment_type
          FROM Rubrics AS R
         WHERE R.key=%(key)s  """,
                  dict(key=key))
   rubrics = cursor.fetchone()
   if rubrics is None:
      info = {}
      rubrics = {}  # pylint: disable=possibly-unused-variable
      print(f"get_questions: no rubrics {key}")
   else:
      assessment_type = rubrics.assessment_type  # pylint: disable=possibly-unused-variable
      info = rubrics.info
      rubrics = editRubrics(rubrics.questions)

   base = renderTemplate(path, **inp.env(), **locals())
   if base.startswith("\n<pre>"):
      # renderTemplate raised an exception
      return base
   base = renderMarkdown(base)

   # Collect up info variables for psform
   exam = inp.info.get("exam")
   register_focus_events = not exam  # psform bit to have mypoll.js register focus events
   autosave = ((request.path.find("/exams/") == 0) or
               (request.path.find("/extracredit/") == 0) or
               (request.path.find("/worksheets/") == 0))
   includeTimer = extended and exam
   exceptions = inp.info.get("exceptions", {})
   info = {**inp.info,
           **exceptions.get(f"_{section}", {}),
           **exceptions.get(onyen, {})}
   result = renderTemplate("psform", **locals())
   # hold the lock for as little time as possible
   if original_onyen == '':
     cursor.execute("""
           INSERT INTO Fetched (time, onyen, key, ip, url)
                        VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                    dict(time=now, onyen=onyen, key=key, ip=ip, url=request.url))
   return result


@app.post("/checklistEntry", name="checklistEntry")
@auth(onyen_is_known)
@with_db_cursor
def checklistEntry(cursor):
   """ Add a checklist entry """
   lecture_date = request.forms.decode('utf-8').lecture_date
   item = request.forms.decode('utf-8').item
   checked = request.forms.decode('utf-8').checked == 'true'
   onyen = request.forms.decode('utf-8').onyen

   if checked:
       # client said this is checked off. Check if key exists and if so, was it submitted
       cursor.execute('''
            SELECT C.key, S.post_id
              FROM checklist_worksheet C
              LEFT JOIN all_submitted S
                ON S.key=C.key AND
                   onyen=%(onyen)s
             WHERE C.item=%(item)s AND
                   C.lecture_date=%(lecture_date)s  ''',
                      dict(item=item, lecture_date=lecture_date, onyen=onyen))
       row = cursor.fetchone()
       if row and row.key and row.post_id is None:
           raise bottle.HTTPError(401,
                                  "Invalid parameter. Assignment not yet submitted")

   cursor.execute("""
       INSERT INTO Checklist (lecture_date, onyen, checked, item, time)
                      VALUES (%(lecture_date)s, %(onyen)s, %(checked)s, %(item)s, %(time)s)
       RETURNING id  """,
                  dict(lecture_date=lecture_date, item=item, checked=checked, time=datetime.now(), onyen=onyen))
   row = cursor.fetchone()
   if row is None:
      log(f"checklist: post not found {lecture_date} {onyen} {checked} {item}")
      not_found(cursor)
   return {}

@app.route("/viewSubmission/<key>", name="viewSubmissionKey")
@auth(onyen_is_known)
@with_db_cursor
@view("viewSubmissionKey")
def viewSubmissionKey(key, cursor):
   """ Show all the user's submisisons for this key """
   onyen, original_onyen = get_onyen_for_endpoint()

   # Use this to limit students seeing grader results
   if key == 'm2-just-material-might-50' and original_onyen == '':
      not_found(cursor)


   cursor.execute("""
        SELECT A.key, A.assessment_type, A.onyen, A.overall_percentage,
               A.number_submissions, A.number_graded
          FROM Assessments A
         WHERE onyen=%(onyen)s AND
               key=%(key)s   """,
                  dict(key=key,
                       onyen=onyen))
   assessment_info = cursor.fetchone()
   if assessment_info is None:
       log(f"viewSubmissionKey: Key {key}, Onyen {onyen} is not known")
       not_found(cursor)

   cursor.execute("""
         WITH S AS (SELECT P.post_id
                      FROM Post AS P, Answers A
                     WHERE P.post_id = A.post_id AND
                           A.field = '_submit' AND
                           A.value like '%%Submit%%' AND
                           P.key = %(key)s AND
                           P.onyen = %(onyen)s),
              N AS (SELECT N.notebook_id
                      FROM Notebooks N
                     WHERE N.key = %(key)s AND
                           N.onyen = %(onyen)s AND
                           N.voided = false),
              G AS (SELECT G.notebook_id, G.url, G.score, G.points_total
                      FROM Notebooks N, Graded_notebooks G
                     WHERE N.key = %(key)s AND
                           N.onyen = %(onyen)s AND
                           N.notebook_id = G.notebook_id AND
                           N.voided = false)

         -- Chrome based assessments
         SELECT S.post_id, COALESCE(F.score, 0) as score, F.msg,
                COALESCE(F.points_total, 0) as points_total, F.elapsed_time
           FROM S
           LEFT JOIN Feedback F ON S.post_id = F.post_id

         UNION

         -- Jupyter notebooks; call it post_id for Order by statement and view
         SELECT N.notebook_id AS post_id, COALESCE(G.score, 0) as score, G.url,
                COALESCE(G.points_total, 0) as points_total, make_interval(mins => 0)
           FROM N
           LEFT JOIN G ON G.notebook_id = N.notebook_id
           ORDER BY post_id  """,
                  dict(onyen=onyen,
                       key=key))
   these_assessments = cursor.fetchall()
   if not these_assessments:
       log(f'viewSubmissionKey: No assessments {key} {onyen}')
       not_found(cursor)

   if original_onyen == '':
       cursor.execute("""
        INSERT INTO Fetched (time, onyen, key, ip, url)
                     VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                      dict(time=datetime.now(), onyen=onyen, key=key, ip=request.remote_addr, url=request.url))

   return dict(onyen=onyen,
               original_onyen=original_onyen,
               assessment_info=assessment_info,
               assessments=these_assessments)


@app.get("/view/<key>", name="viewKey")
@auth(onyen_is_known)
@with_db_cursor
@view("listSubmissions")
def list_submissions(key, cursor):
   """
   Allow them to list their submissions
   """
   onyen, original_onyen = get_onyen_for_endpoint()
   # Get the time, id, assessment_type, whetherSubmitted, and number of grades
   cursor.execute("""
        SELECT P.time, P.post_id, R.assessment_type,
                             EXISTS(SELECT 1
                                      FROM Answers AS A
                                     WHERE P.post_id = A.post_id AND
                                           A.field='_submit' AND
                                           A.value = 'Submit') as wassubmitted,
                             (SELECT count(DISTINCT P.key)
                                FROM Answers AS A, Post AS P
                               WHERE A.value='unsubmitted' AND
                                     P.post_id = A.post_id AND
                                     P.onyen = %(onyen)s AND
                                     A.field='_submit') as graceCounts
          FROM Post AS P, Rubrics AS R
         WHERE P.onyen = %(onyen)s AND
               R.key = P.key AND
               P.key = %(key)s
         ORDER BY P.time, P.post_id  """,
                  dict(onyen=onyen, key=key))
   posts = cursor.fetchall()
   if len(posts) == 0:
       log(f'list_submissions: onyen {onyen} requested list of submissions for key {key}, but none exist')
       not_found(cursor)
   return dict(onyen=onyen, is_admin=onyen_is_admin(original_onyen), key=key, posts=posts)


def get_page_section(cursor, onyen, page_section):
    ''' Given an onyen, what key's have page_section access '''
    # I gotta get rid of active pages as an array!
    cursor.execute('''
         with Ids as (select P.id
                        from pages P, roll R
                       where R.onyen=%(onyen)s and
                             (P.onyen=R.onyen or (P.onyen = '' and P.section=R.section)) and
                             start_time < now() and
                             end_time > now()
                             order by P.onyen desc -- Prefer access page for onyen over section
                             limit 1               -- Only get the first access page
                      )

         select DISTINCT key
           from pages P, ids I, active_sections A
          where P.id=I.id and
                P.id=A.page_id and
                A.page_section = %(page_section)s
          order by key ''',
                   dict(onyen=onyen, page_section=page_section))
    return [x.key for x in cursor.fetchall()]


@app.post("/submit/<key>", name="answer")
@auth(onyen_is_known)
@with_db_cursor
@view("post_successful")
@allow_json
def post_answer(key, cursor):
   """
    Accept a post and store the fields in the db
   """
   now = datetime.now()
   onyen, _ = get_onyen_for_endpoint()
   cursor.execute("""
        SELECT R.zwsp, R.exam_time, R.section
          FROM Roll as R
         WHERE R.onyen = %(onyen)s  """,
                  dict(onyen=onyen))
   row = cursor.fetchone()
   zwsp = row and row.zwsp
   section = row and row.section

   # Is this submit valid?
   if not section:
      log(f"post_answer: {onyen} not enrolled in COMP421.")
      not_allowed()
   pages = get_active_pages(cursor, key, onyen)

   ip = request.remote_addr
   cursor.execute("""
        INSERT INTO Post (time, onyen, key, ip)
                  VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s)
                  RETURNING post_id  """,
                  dict(time=now, onyen=onyen, key=key, ip=ip))
   post_id = cursor.fetchone()[0]
   form = request.forms.decode('utf-8')
   fields = [(post_id, fieldname, value) for fieldname, value in form.items()]
   checkZWSP(fields, onyen, zwsp, key, post_id, cursor)
   cursor.executemany("""
        INSERT INTO Answers (post_id, field, value)
                     VALUES (%s, %s, %s)   """,
                      fields)
   # Commit this submit so that if another submit comes along our later
   # code will see the committed answers from both submissions
   cursor.connection.commit()

   # Did the user submit while the submit flag was off?
   this_is_a_submit = (post_id, '_submit', 'Submit') in fields
   if this_is_a_submit and not submit_in_pages(pages):
      log(f"post_answer: Onyen {onyen}, section {section} has pages {pages} w/out submit at time {now}")
      cursor.execute("""
            UPDATE Answers
               SET value = 'no_submit_button'
             WHERE post_id = %(post_id)s AND
                   field = '_submit'  """,
                     dict(post_id=post_id))
      cursor.connection.commit()
      raise bottle.HTTPError(405, f'Sorry {onyen}, submit is not available for {key} at time {now}')

   # Check if the student has already ungraded submission, or a 100% graded submission if so reject this one
   if this_is_a_submit:
       cursor.execute("""
            SELECT count(*) AS count
              FROM Post P, Answers A
             WHERE P.post_id = A.post_id AND
                   A.value = 'Submit' and
                   A.field = '_submit' AND
                   P.key = %(key)s AND
                   P.onyen = %(onyen)s AND
                   P.post_id < %(post_id)s  """,
                      dict(post_id=post_id,
                           key=key,
                           onyen=onyen))
       previous_posts = cursor.fetchone()[0] # Used later for number of submissions ungraded
       cursor.execute("""
            -- Need to get the assessment_type in case there is no tuple in Assessments
            WITH temp AS (SELECT key, assessment_type
                            FROM Rubrics
                           WHERE key=%(key)s),
            -- Get the assessment information for the left join 
                 temp2 AS (SELECT *
                            FROM Assessments
                           WHERE key=%(key)s AND
                                 onyen=%(onyen)s)

            -- Coalesce the potentially null values needed
            SELECT temp.assessment_type, COALESCE(overall_percentage, 0) as overall_percentage,
                   COALESCE(number_submissions, 0) as number_submissions,
                   COALESCE(one_submission_graded_100_percent, False) as one_submission_graded_100_percent,
                   COALESCE(number_graded, 0) as number_graded
              FROM temp LEFT JOIN temp2 ON temp.key=temp2.key and
                                           temp.assessment_type=temp2.assessment_type  """,
                      dict(key=key,
                           onyen=onyen))
       assessment_info = cursor.fetchone()
       if assessment_info.one_submission_graded_100_percent:
           # You can only submit once and get a 100%
           log(f"post_answer: Onyen {onyen}, section {section}, key {key} already has 100% submission")
           cursor.execute("""
                 UPDATE Answers
                    SET value = 'already_one_100_percent'
                  WHERE post_id = %(post_id)s AND
                        field = '_submit'  """,
                          dict(post_id=post_id))
           cursor.connection.commit()
           raise bottle.HTTPError(405, f'Sorry {onyen}, you already have an assessment for {key} with a grade of 100%')

       if assessment_info.number_submissions > max_submissions:
           # Including this submission, there can only 10 submissions
           log(f"post_answer: Onyen {onyen}, section {section}, key {key} has ",
               f"{assessment_info.number_submissions} submissions already")
           cursor.execute("""
                 UPDATE Answers
                    SET value = 'too_many_submissions'
                  WHERE post_id = %(post_id)s AND
                        field = '_submit'  """,
                          dict(post_id=post_id))
           cursor.connection.commit()
           raise bottle.HTTPError(405, f'Sorry {onyen}, for {key}, has {assessment_info.number_submissions} already')

       # If the assessment's table's tally of the number of submission or if
       # two posts done in a race s.t. the assesment is not yet created so check the previous submissions
       log(f'post_answer: JJM number_submissions {assessment_info.number_submissions}',
           f'post_id={post_id}',
           f' number_graded {assessment_info.number_graded} previous_posts {previous_posts}')
       if assessment_info.number_submissions > assessment_info.number_graded or \
             previous_posts > assessment_info.number_graded+1:
           # Including this submission, there can only be one more submitted than graded
           # User onyen has an ungraded submission! Do not accept submission!
           cursor.execute("""
              SELECT P.post_id
                FROM Post P, Answers A
               WHERE P.post_id=A.post_id AND
                     P.post_id != %(post_id)s AND -- Not the current submission!
                     NOT EXISTS(SELECT F.post_id
                                  FROM Feedback F
                                 WHERE F.post_id = P.post_id) AND
                     A.field='_submit' AND
                     A.value='Submit' AND
                     P.key = %(key)s AND
                     P.onyen = %(onyen)s   """,
                          dict(onyen=onyen,
                               post_id=post_id,
                               key=key))
           rows = cursor.fetchall()
           post_ids = ', '.join([f'{x.post_id}' for x in rows])
           log(f"post_answer: Onyen {onyen}, section {section}, key {key} has post_id's",
               f"{post_ids} have not been graded yet")
           cursor.execute("""
                 UPDATE Answers
                    SET value = 'ungraded_exists'
                  WHERE post_id = %(post_id)s AND
                        field = '_submit'  """,
                          dict(post_id=post_id))
           cursor.connection.commit()
           raise bottle.HTTPError(405, f'Sorry {onyen}, for {key}, you have submissions that have not yet been graded')

       if assessment_info.number_submissions == 0 and not first_submit_in_pages(pages):
           # This is only open for partial submits (subsequent pages)
           log(f'post_answer: Onyen {onyen} trying to subsequent submit {key} {post_id} w/out first submit in class: {pages}')
           cursor.execute("""
                 UPDATE Answers
                    SET value = 'attempted_subsequent_without_original'
                  WHERE post_id = %(post_id)s AND
                        field = '_submit'  """,
                          dict(post_id=post_id))
           cursor.connection.commit()
           raise bottle.HTTPError(405, f'Sorry {onyen}, for {key} you needed to submit this before the original submit deadline')

       # check if no submit code is required or if it is, is it valid
       valid = not submit_code_in_pages(pages) or \
           ("_submitCode" in form and validateSubmitCode(cursor, form['_submitCode']))
       if valid:
          cursor.execute("""
            INSERT INTO Assessments (key, assessment_type, onyen,
                                     overall_percentage, number_submissions, number_graded)
                            VALUES(%(key)s, %(assessment_type)s, %(onyen)s,
                                    0, %(number_submissions)s, 0)
               ON CONFLICT(key, onyen) DO UPDATE
                              SET number_submissions=%(number_submissions)s  """,
                         dict(key=key,
                              assessment_type=assessment_info.assessment_type,
                              number_submissions=assessment_info.number_submissions+1,
                              onyen=onyen))
          submission_url = get_url('viewSubmission', key=key, post_id=post_id)
          cursor.connection.commit()
          now = datetime.now()
          redirect(submission_url)
       else:  # invalid submit code
           log(f"post_answer: Invalid submit code for post_id {post_id}")
           cursor.execute("""
                 UPDATE Answers
                    SET value = 'invalid_submit_code'
                  WHERE post_id = %(post_id)s AND
                        field = '_submit'  """,
                          dict(post_id=post_id))
           cursor.connection.commit()

   return {"onyen": onyen, "key": key, "valid": not this_is_a_submit}




@app.get("/view/<key>/<post_id:int>", name="viewSubmission")
@auth(onyen_is_known)
@with_db_cursor
@view("viewSubmission")
def view_submission(key, post_id, cursor):
   """
   Allow them to see their previous submissions
   """
   onyen, original_onyen = get_onyen_for_endpoint()

   # Use this to limit students seeing grader output
   if key == 'm2-just-material-might-50' and original_onyen == '':
      not_found(cursor)

   # Do not show _[a-z] fields as these are reserved like _onyen or _calculator
   # Do show things like _Insert which have to have the _ to denote no response from SQL Inserts
   cursor.execute("""
        SELECT A.field, A.value, P.time, R.assessment_type
          FROM Post AS P, Answers AS A, Rubrics AS R
         WHERE P.onyen = %(onyen)s AND
               P.key = %(key)s AND
               P.post_id = %(post_id)s AND
               P.post_id = A.post_id AND
               P.key = R.key AND
               (SUBSTRING(A.field FROM 1 FOR 1) != '_' or
                SUBSTRING(A.field FROM 2 FOR 1) != LOWER(SUBSTRING(A.field FROM 2 FOR 1)))
         ORDER BY A.field  """,
                  dict(onyen=onyen, key=key, post_id=post_id))
   submission_values = cursor.fetchall()
   if len(submission_values) == 0:
      log(f"view_submission onyen={onyen} key={key} post_id={post_id} values={submission_values}")
      not_found(cursor)

   # Get graded output
   cursor.execute("""
        SELECT score, msg, points_total, elapsed_time
          FROM Feedback
         WHERE post_id = %(post_id)s  """,
                  dict(post_id=post_id))
   graded_output = cursor.fetchone()

   # Get the url of the assessment source
   source_url = ''
   for folder in assessment_folders:
      file = glob.glob(f"content/{folder}/{key}.tmd")
      if  len(file) > 0:
         source_url = get_url(folder, key=key)
   return {"onyen": onyen, "key": key, "post_id": post_id, "submission_values": submission_values,
           "graded_output": graded_output, "source_url": source_url}


@app.get("/view", name="view")
@auth(onyen_is_known)
@with_db_cursor
@view("listKeys")
def list_keys(cursor):
   """
    Allow them to list their submissions
    """
   onyen, _ = get_onyen_for_endpoint()
   cursor.execute("""
        SELECT DISTINCT key
          FROM Post AS P
         WHERE P.onyen = %(onyen)s  """,
                  dict(onyen=onyen))
   keys = cursor.fetchall()

   # Find all the homeworks in a single query:
   cursor.execute("""
       SELECT H.key,
              N.notebook_id,
              G.url,
              CASE WHEN G.score IS NULL THEN 0 ELSE G.score END,
              CASE WHEN G.points_total IS NULL THEN 0 ELSE G.points_total END
         FROM Valid_Homeworks(%(onyen)s) as H
         LEFT JOIN Notebooks N
            ON N.key = H.key AND
               N.notebook_id in (SELECT min(notebook_id)
                                   FROM Notebooks
                                  WHERE onyen=%(onyen)s
                                  GROUP BY key) AND
               N.onyen = %(onyen)s
         LEFT JOIN graded_notebooks G
         ON N.notebook_id = G.notebook_id   """,
                  dict(onyen=onyen))
   return dict(onyen=onyen, keys=keys, homeworks=cursor.fetchall())



@app.post("/browser/<event>", name="browser")
@auth(onyen_is_known)
@with_db_cursor
def focus(cursor, event):
   """Record focus changes"""
   onyen, _ = get_onyen_for_endpoint()
   now = datetime.now()
   first_dash_pos = event.find('-')
   if first_dash_pos > 0:
      key = event[first_dash_pos+1:]
      event = event[:first_dash_pos]
   else:
      key = ''
   cursor.execute("""INSERT INTO Browser (time, onyen, event, key)
                                 VALUES (%(time)s, %(onyen)s, %(event)s, %(key)s)""",
                  dict(time=now, onyen=onyen, event=event, key=key))
   return "OK"


@app.get("/feedback", name="feedback")
@auth(onyen_is_known)
@with_db_cursor
@view("feedback")
def feedback(cursor):
   """Display feedback"""
   onyen, _ = get_onyen_for_endpoint()

   # Get each submission, points info if graded, and answers if available
   cursor.execute("""
        SELECT P.post_id, P.time, P.key, F.score, F.msg, F.points_total,
               Answers_exist_for_user_and_key(%(onyen)s, P.key) as answers_exist
          FROM (SELECT P.post_id, P.time, P.key
                  FROM Post AS P, Answers AS A
                 WHERE P.onyen = %(onyen)s AND
                       P.post_id = A.post_id AND
                       A.field = '_submit' AND
                       A.value = 'Submit') AS P
          LEFT JOIN Feedback AS F ON P.post_id = F.post_id
         ORDER BY P.key ASC, F.score DESC, P.time DESC""",
                  dict(onyen=onyen))
   all_feedbacks = cursor.fetchall()
   return dict(onyen=onyen, feedbacks=all_feedbacks)


@app.get("/rubric/<key>", name="rubric")
@auth(onyen_is_known)
@with_db_cursor
@view("viewRubric")
def viewRubric(key, cursor):
   """Display answers"""
   onyen, _ = get_onyen_for_endpoint()
   # if key=='fe-mothball-midwife-granite-27':
   #    not_found(cursor)

   # ensure this user has a graded submission
   if not onyen_is_admin(onyen):
      cursor.execute("""
           SELECT EXISTS (SELECT F.score
                            FROM Post AS P, Feedback AS F
                           WHERE P.onyen = %(onyen)s AND
                                 F.post_id = P.post_id AND
                                 P.key = %(key)s) """,
                     dict(onyen=onyen, key=key))
      exists = cursor.fetchone().exists
      if not exists:
         log(f"Answers: onyen {onyen} requested answers for assessment {key} that doesn't exist")
         not_found(cursor)

   # get the answers as a json formatted string
   cursor.execute("""
        SELECT R.info, R.questions
          FROM Rubrics AS R
         WHERE R.key = %(key)s  """,
                  dict(key=key))
   row = cursor.fetchone()  # Has to exist because grading done
   if not row or len(row) == 0:
      not_found(cursor)

   # return values which is dict( question: answer )
   rubric = row.questions
   # Do not show _[a-z] fields as these are reserved like _onyen or _calculator
   # Do show things like _Insert which have to have the _ to denote no response from SQL Inserts
   values = {key: rubric[key]['solution'] for key in rubric.keys()
             if key[0:2] != f'_{key[1].lower()}'}

   cursor.execute("""
      INSERT INTO Fetched (time, onyen, key, url)
                   VALUES (%(time)s, %(onyen)s, %(key)s, %(url)s)  """,
                  dict(time=datetime.now(), onyen=onyen, key=key, url=request.url))
   return {"values": values, "key": key}



@app.get("/slides/<slide_name:path>", name="slides")
@auth(onyen_is_known)
@with_db_cursor
def slide(cursor, slide_name):
   """Redirect to the local slide filename. """
   onyen, _ = get_onyen_for_endpoint()
   now = datetime.now()
   ip = request.remote_addr

   slide_path = f'slides/{slide_name}'
   if not osp.exists(slide_path):
      log(f' slide {slide_name} not found at {slide_path}')
      not_found(cursor)

   cursor.execute("""
      INSERT INTO Fetched (time, onyen, key, ip, url)
                   VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                  dict(time=now, onyen=onyen, key=slide_name, ip=ip, url=request.url))
   return static_file(slide_path, root='.')


@app.get("/video/<video_name:path>", name="video")
@auth(onyen_is_known)
@with_db_cursor
def video(cursor, video_name):
   """Redirect to the local video filename. video_name does not include mp4   """
   onyen, _ = get_onyen_for_endpoint()
   now = datetime.now()
   ip = request.remote_addr

   if video_name == 'CourseCare':
      # course care is 481749f5-4309-4cb7-9d4c-ac8e001ae92e
      hexcode = '481749f5-4309-4cb7-9d4c-ac8e001ae92e'
      url = f"https://uncch.hosted.panopto.com/Panopto/Pages/Viewer.aspx?id={hexcode}"

      cursor.execute("""
        INSERT INTO Fetched (time, onyen, key, ip, url)
                     VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                     dict(time=now, onyen=onyen, key=url, ip=ip, url=request.url))
      cursor.connection.commit()

      redirect(url)

   if not osp.exists(f'static/videos/{video_name}.mp4'):
      log(f' video {video_name} not found')
      not_found(cursor)

   cursor.execute("""
      INSERT INTO Fetched (time, onyen, key, ip, url)
                   VALUES (%(time)s, %(onyen)s, %(key)s, %(url)s)  """,
                  dict(time=now, onyen=onyen, key=video_name, ip=ip, url=request.url))
   return static_file(f'{video_name}.mp4', root='./static/videos/')



class ReverseProxied:  # pylint: disable=too-few-public-methods
   """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location ~* ^/([0-9]+) { # encoding the port number in the URI
        proxy_pass http://127.0.0.1:$1/; # forward to that port
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /$1; # pass the port number to the app
        }

    :param app: the WSGI application

    hacked from: http://flask.pocoo.org/snippets/35/ and
    https://stackoverflow.com/questions/25106424/nginx-proxy-redirection-with-port-from-uri
    """

   def __init__(self, the_app):
       self.app = the_app

   def __call__(self, environ, start_response):
      script_name = environ.get("HTTP_X_SCRIPT_NAME", "")
      if script_name:
         environ["SCRIPT_NAME"] = script_name
         path_info = environ["PATH_INFO"]
         if path_info.startswith(script_name):
            environ["PATH_INFO"] = path_info[len(script_name) :]
         elif path_info == "/":
            environ["PATH_INFO"] = ""

      scheme = environ.get("HTTP_X_SCHEME", "")
      if scheme:
         environ["wsgi.url_scheme"] = scheme
      return self.app(environ, start_response)

# pylint: disable=unused-import, wrong-import-position
# Include administration endpoints
from appadmin import (ungraded, welcome, submittables, visualizations, assessments,
                      get_student_answers, get_answers, newSubmitCode, mathjax,
                      notes, get_roll, videos, worksheet_bonus, worksheet_bonus_submit,
                      get_stats, unsubmit)
# Include SQL interpreter support
from appsql import sql_interpreter, list_sql_interpreter

if __name__ == "__main__":
   Testing = True
   serve()
