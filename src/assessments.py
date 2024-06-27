"""
 Describe and list the assessments for COMP 550
"""
# pylint: disable=too-many-arguments, unsupported-membership-test, too-many-statements, bad-indentation
from datetime import date
import sys
from collections import namedtuple
from itertools import compress
from statistics import mean


SUBMITTABLE_PAGES = ["submit_code_req", "submit_no_code", "subsequent_submit_no_code"]
FIRST_SUBMITTABLE_PAGES = ["submit_code_req", "submit_no_code"]

drops = dict(worksheet=1, homework=0, game=0,
             fe=0, midterm1=0, midterm2=0)
max_submissions = 10
def assessments_matching(assessments, field, value):
    '''Return the assessments with fields matching the key'''
    this_boolean = [getattr(x, field) == value for x in assessments]
    these_assessments = list(compress(assessments, this_boolean))
    return these_assessments

def get_assessment_percentages(cursor, onyen):
   ''' Given an onyen, return the percentages for each type of assessment '''
   cursor.execute("""
      WITH weights AS (SELECT worksheets, games, homeworks, midterm1, midterm2, fe, 
                              RANK() OVER(PARTITION BY onyen
                                              ORDER BY onyen) AS ranknum
                         FROM assessment_percentages
                        WHERE onyen is Null OR
                              onyen = %(onyen)s)

      SELECT worksheets, games, homeworks, midterm1, midterm2, fe
        FROM weights
       WHERE ranknum=1""",
                  dict(onyen=onyen))
   per = cursor.fetchone()
   # assert per and sum(per) == 101, f"For onyen {onyen}, the percentages are {per}"
   return per

def get_assessment_due_date(cursor, key, onyen):
    """ Given a key return the latest date/time the assessment can be submitted

        Caller expects a datetime object even if there is no due date.
        In that case, return the first day of classes

        Note that first you find the single page record for the
        onyen or section (prefer onyen), then see what page
        sections apply
    """
    cursor.execute("""
        WITH Ids AS (SELECT P.id, RANK() OVER(Partition by P.key     -- rank within each key
                                              Order BY P.onyen DESC) -- prefer onyen page
                                              AS rank_num
                       FROM Pages as P, Roll R
                      WHERE R.onyen = %(onyen)s AND
                            P.key = %(key)s AND
                            (P.onyen=%(onyen)s OR (P.onyen='' AND P.section=R.section)))

        SELECT P.end_time
           FROM Active_sections as A, Pages as P, Ids as I
           WHERE A.page_id = P.id AND
                 A.page_id = I.id AND
                 ((A.page_section in %(subsequent_submittable_pages)s and
                   -- did they originally submit
                   (SELECT EXISTS (SELECT *
                                     FROM Assessments
                                    WHERE key=%(key)s AND
                                          number_submissions > 0 AND 
                                          onyen=%(onyen)s))) OR
                  A.page_section in %(first_submittable_pages)s) AND
                 I.rank_num = 1
           ORDER BY P.end_time DESC        """,
                   dict(key=key, onyen=onyen,
                        subsequent_submittable_pages=tuple(SUBMITTABLE_PAGES),
                        first_submittable_pages=tuple(FIRST_SUBMITTABLE_PAGES)))
    rows = cursor.fetchall()
    if not rows or not rows[0]:
       return date.today
    return rows[0].end_time


def get_active_pages(cursor, key, onyen):
    """ Given a key return all the active pages for the onyen

        Note that first you find the single page record for the
        onyen or section (prefer onyen), then see what page
        sections apply
    """
    cursor.execute("""
        WITH Ids AS (SELECT P.id, RANK() OVER(Partition by P.key     -- rank within each key
                                              Order BY P.onyen DESC) -- prefer onyen page
                                              AS rank_num
                       FROM Pages as P, Roll R
                      WHERE R.onyen = %(onyen)s AND
                            P.key = %(key)s AND
                            P.start_time <= now() AND  -- include start_time
                            P.end_time > now() AND     -- exclude end_time
                            (P.onyen=%(onyen)s OR (P.onyen='' AND P.section=R.section)))

        SELECT A.page_section
           FROM Active_sections as A, Pages as P, Ids as I
           WHERE A.page_id = P.id AND
                 A.page_id = I.id AND
                 I.rank_num = 1  """,
                   dict(key=key, onyen=onyen))
    rows = cursor.fetchall()
    if not rows:
        return []

    pages = [x.page_section for x in rows]
    assert len(set(pages)) == len(pages), f'For {key}, {onyen} duplicate pages in {pages}'
    assert not has_multiple_submits(pages), f'For {key}, {onyen} multiple submits in {pages}'
    return pages

def submit_in_pages(pages):
    """ Return true if the pages have a valid submit page section turned on at this time """
    return any(x in SUBMITTABLE_PAGES for x in pages)

def subsequent_submit_in_pages(pages):
    """ Return true if the pages have a valid subsequent submit page section turned on at this time """
    return any(x == 'subsequent_submit_no_code' for x in pages)

def first_submit_in_pages(pages):
    """ Return true if the pages have a valid first sub page section turned on at this time """
    return any(x in ['submit_no_code', 'submit_code_req'] for x in pages)

def has_multiple_submits(list_of_pages):
   '''Given a list of valid pages, check for duplicates'''
   if 'submit_code_req' in list_of_pages and \
         'submit_no_code' in list_of_pages:
      return True
   return False

def remove_submit_from_pages(pages):
    """ Remove any submittable in pages from the pages """
    for x in SUBMITTABLE_PAGES:
        if x in pages:
            pages.remove(x)
    return pages

def submit_code_in_pages(pages):
    """ Return true if the pages say a submit code is required """
    return any(x == "submit_code_req" for x in pages)

def assessments_sorted(assessments, field, minimum_number=0, reverse=False):
    '''Return the assessments as a list sorted by the field
    If there are less than minimum_number of elements, add None to the list'''
    sorted_assessments = sorted(assessments, key=lambda x: getattr(x, field), reverse=reverse)
    if minimum_number > 0:
       sorted_assessments = sorted_assessments + [None]*minimum_number
       sorted_assessments = sorted_assessments[:minimum_number]
    return sorted_assessments

GameBonusInfo = namedtuple('GameBonusInfo', 'reason sort_descending assessment_field podium_size')
games = dict(crime=[GameBonusInfo(reason='Fifty shortest elapsed time',
                                  podium_size=50,
                                  sort_descending=False,
                                  assessment_field='elapsed_time')],
             sailors=[GameBonusInfo(reason='Fifty shortest elapsed time',
                                    podium_size=50,
                                    sort_descending=False,
                                    assessment_field='elapsed_time')],
             nuclear=[GameBonusInfo(reason='Fifty shortest elapsed time',
                                    podium_size=50,
                                    sort_descending=False,
                                    assessment_field='elapsed_time')]
             )

def log(*args):
   """Print for debugging"""
   print(*args, file=sys.stderr)

def get_all_worksheet_bonuses(cursor, onyen):
   ''' Single point for all the worksheet bonuses'''
   cursor.execute("""
       SELECT W.share_time, W.reason, W.points
         FROM Worksheet_bonus AS W
        WHERE W.onyen=%(onyen)s
        ORDER BY W.share_time ASC """,
                  dict(onyen=onyen))
   return cursor.fetchall()

def get_all_game_bonuses(cursor, onyen):
   ''' Single point for all the game bonuses'''
   cursor.execute("""
       SELECT G.onyen, G.reason, G.key, G.points, G.explanation
         FROM Game_bonus AS G
        WHERE G.onyen=%(onyen)s
        ORDER BY G.key, G.reason ASC """,
                  dict(onyen=onyen))
   return cursor.fetchall()

def get_all_assessments(cursor, onyen):
   '''Find all assessments and their scores for user onyen'''
   cursor.execute("""
       SELECT A1.key, A1.assessment_type,
              COALESCE(A2.overall_percentage, 0) as overall_percentage,
              COALESCE(A2.one_submission_graded_100_percent, false) as one_submission_graded_100_percent,
              COALESCE(A2.number_graded, 0) as number_graded,
              COALESCE(A2.number_submissions, 0) as number_submissions
         FROM All_assessments(%(onyen)s) AS A1
         LEFT JOIN Assessments AS A2 ON A1.key = A2.Key AND A2.onyen=%(onyen)s
        ORDER BY A1.assessment_type, A1.key  """,
                  dict(onyen=onyen))
   return cursor.fetchall()


def get_all_game_assessments(cursor, key, section=None):
    ''' Given a key like game-crime, find all the assessments for game-crime-1, etc '''
    cursor.execute("""
        SELECT S.post_id, S.key, S.onyen, R.game_alias_name, F.score, F.msg, F.points_total, F.elapsed_time, R.section
          FROM All_Submitted AS S, Feedback AS F, Post AS P, Roll R
         WHERE S.post_id=F.post_id AND  -- Join Post, Feedback, submitted, team tables
               P.post_id=F.post_id AND
               P.onyen=R.onyen AND
              (R.section=%(section)s or %(section)s is Null) and
               F.msg = 'All correct' AND -- Only want actual 100 not just 76 percent or better
               S.Key like %(key)s  -- Only want this assessment
         ORDER BY S.key, F.elapsed_time  """,
                   dict(key=f'{key}-%', section=section))
    return cursor.fetchall()

def get_score(a, this_type, this_bonuses=0, this_drops=0, extra_bonus=False):
   ''' Compute the score for the assessment type
    Note: if extra_bonus is specified it should be an array of bonuses to be applied.
          Extra_bonus is extra because it can add to a 100% score
   '''
   # Get the worksheet score
   these_assessments = compress(a, [x.assessment_type == this_type for x in a])
   scores = sorted(x.overall_percentage for x in these_assessments)

   if this_drops and this_drops < len(scores):
      scores = scores[this_drops:]  # Assumes scores are sorted ASC

   if this_bonuses > 0:
       if extra_bonus:
           # Add bonus to any score
           scores = sorted(scores, reverse=True)
           for index in range(min(len(extra_bonus), len(scores))):
               scores[index] += extra_bonus[index].points
       else:
           # Bonus can only add to <= 100 points
           scores = sorted(scores)
           # Run the for loop for as many bonuses or worksheets submitted.
           # If you have 5 bonuses, but only 1 worksheet, only one bonus will apply
           for index in range(min(this_bonuses, len(scores))):
              scores[index] = min(100, 50+scores[index])

   if len(scores) == 0:
       return 0
   return round(mean(scores), 2)

def updateGrades(cursor, onyen):  # pylint: disable=too-many-branches, too-many-statements
   ''' Update the grades table for a student '''

   cursor.execute('''
         --- Insert this onyen into roll section 000, to say they're not in the class
         INSERT INTO Roll (onyen, section, name)
                SELECT %(onyen)s, '000', 'unknown, unknown'
                WHERE NOT EXISTS (SELECT onyen -- Only if they are not in the class
                                    FROM Roll
                                   WHERE onyen=%(onyen)s ) ''',
                  dict(onyen=onyen))

   cursor.execute("""SELECT graduate_student
                   FROM Roll
                  WHERE onyen=%(onyen)s""",
                  dict(onyen=onyen))
   row = cursor.fetchone()
   graduate_student = row and row.graduate_student

   assessments = get_all_assessments(cursor, onyen)
   worksheet_bonuses = get_all_worksheet_bonuses(cursor, onyen)
   game_bonuses = get_all_game_bonuses(cursor, onyen)

   ws = get_score(assessments, 'worksheet',
                  this_bonuses=len(worksheet_bonuses), this_drops=drops['worksheet'])
   game = get_score(assessments, 'game', extra_bonus=game_bonuses,
                    this_bonuses=len(game_bonuses))

   hwk = get_score(assessments, 'homework', this_drops=drops['homework'])
   m1 = get_score(assessments, 'midterm1', this_drops=drops['midterm1'])
   m2 = get_score(assessments, 'midterm2', this_drops=drops['midterm2'])
   fe = get_score(assessments, 'fe', this_drops=drops['fe'])

   percentage = get_assessment_percentages(cursor, onyen)
   total = (round(fe * percentage.fe / 100, 2) +
            round(m2 * percentage.midterm2 / 100, 2) +
            round(m1 * percentage.midterm1 / 100, 2) +
            round(hwk * percentage.homeworks / 100, 2) +
            round(ws * percentage.worksheets / 100, 2) +
            round(game * percentage.games / 100, 2))
   total = round(total, 2)
   total = min(100, round(total, 2))

   if total >= 94.78: # 95
      letter_grade = 'A'
   elif total >= 89.82: # 90
      letter_grade = 'A-'
   elif total >= 86 + 1/3:  # 86 + 1/3
      letter_grade = 'B+'
   elif total >= 83 + 1/3:
      letter_grade = 'B'
   elif total >= 79.25: # 80:
      letter_grade = 'B-'
   elif total >= 76 + 2/3:
      letter_grade = 'C+'
   elif total >= 73.3: # JJM 73 + 1/3:
      letter_grade = 'C'
   elif total >= 69.9: # JJM 70:
      letter_grade = 'C-'
   elif total >= 64.9: # JJM 65:
      letter_grade = 'D+'
   elif total >= 60:
      letter_grade = 'D'
   else:
      letter_grade = 'F'

   # Assume there are only one fe assessment
   submitted_finals = list(compress(assessments, [x.assessment_type == 'fe' for x in assessments]))
   if len(submitted_finals) == 0 or submitted_finals[0].number_submissions == 0:
       # There were no submission (id is None) for finals for this student
       if total + percentage.fe > 60 and not graduate_student:
           letter_grade = 'AB'
       else:
           letter_grade = 'FA'
   if graduate_student:
      if total >= 90:
         letter_grade = 'H'
      elif total >= 80:
         letter_grade = 'P'
      elif total >= .70:
         letter_grade = 'L'
      else:
         letter_grade = 'F'

   cursor.execute("""delete from grades where onyen = %(onyen)s""", {"onyen": onyen})
   cursor.execute("""
       insert into grades
          (onyen, letterGrade, total, fe,
           midterm1, midterm2,
           homeworks, worksheets, games)
       values (%(onyen)s, %(letterGrade)s, %(total)s, %(fe)s,
               %(midterm1)s, %(midterm2)s,
               %(homeworks)s, %(worksheets)s, %(games)s
              )
       ON CONFLICT (onyen) DO UPDATE SET
            letterGrade = %(letterGrade)s, total = %(total)s,
            fe = %(fe)s, midterm2 = %(midterm2)s,
            midterm1 = %(midterm1)s,
            homeworks = %(homeworks)s, worksheets=%(worksheets)s, games=%(games)s;
         """,
                  {"onyen": onyen, "letterGrade": letter_grade, "total": total, "fe": fe,
                   "midterm1": round(m1, 2), "midterm2": round(m2, 2),
                   "homeworks": hwk, "worksheets": ws, "games": game})
