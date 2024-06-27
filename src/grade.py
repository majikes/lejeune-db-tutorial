#!/usr/bin/env python3
"""Incrementally grade assignments for mypoll"""
# pylint: disable=too-many-arguments, too-many-branches, unused-argument, redefined-outer-name, too-many-statements
# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation

import re
from datetime import datetime

import Args
import db
from assessments import updateGrades
from evalInContext import evalMultiple
from wagnerfischerpp import WagnerFischer


#  This block comment is no longer valid with multiple submissions
# Note:  changed field='_submit" and value='Submit' to
# field='_submit' and value like '%%Submit%%' due to copying
# codes, ZWSPs get appended to the submit field

def get_feedback(cursor, key, onyen, post_id, theirAnswers, rubrics, result, info):
   """Given a graded assessment, take their answers and the rubric and return the result"""

   # Calculate the items that are correct
   correct = {tag: result[tag].get("correct", False) for tag in result
                                                     if tag in theirAnswers}
   partially_correct = {tag : result[tag].get("tests", []) for tag in result
                        if (tag in correct and not correct[tag] and
                            result[tag].get('partial_credit', False) and
                            tag in theirAnswers)}

   # Compute their score and their points total
   points_total = info.get("points_total", 100)
   points_limit = info.get("points_limit", points_total)
   score = min(points_limit,
               points_total - sum(
                  rubrics[K]["points"] for K in rubrics.keys()
                  if (K not in correct or not correct[K])))
   points_total = min(points_total, points_limit)
   feedback = ", ".join(K for K in rubrics.keys()
                        if (K in correct and
                            K[0] != '_' and
                            not correct[K]))

   # Add in partial test cases
   for q in partially_correct:
      number_tests = len(partially_correct[q])
      number_correct = len([i for i in range(number_tests) if partially_correct[q][i].get('correct', False)])
      if number_correct > 0:
         # Remove item from feedback
         feedback = re.sub(q+',', '', feedback)
         feedback = re.sub(q, '', feedback)
         feedback += f' {q} partially {number_correct} / {number_tests+1}, '
         partial_points = round(rubrics[q]['points'] * number_correct / (number_tests +1), 2)
         score = min(points_limit, score + partial_points)

   # Do any modifications that you may want to make on a per assessment basis
   # Old way of doing it:
   # if key == 'm1-farm-example-scale-34':
   #     if user in ['tanatc', 'maddk', 'antud', 'amarlett']:
   #         q = 'Three.Pointers.1'
   #         if q in correct and not correct[q]:
   #             feedback = re.sub(q+',', '', feedback)
   #             feedback = re.sub(q, '', feedback)
   #             correct[q] = True
   #             score += rubrics[q]['points']
   #     if user in ['hyunda']:
   #         q = 'Three.Pointers.2'
   #         if q in correct and not correct[q]:
   #             feedback = re.sub(q+',', '', feedback)
   #             feedback = re.sub(q, '', feedback)
   #             correct[q] = True
   #             score += rubrics[q]['points']
   #     if user in ['ysheng04']:
   #         q = 'Three.Pointers.3'
   #         if q in correct and not correct[q]:
   #             feedback = re.sub(q+',', '', feedback)
   #             feedback = re.sub(q, '', feedback)
   #             correct[q] = True
   #             score += rubrics[q]['points']


   if key in ['worksheet-game-nuclear-01', 'worksheet-game-nuclear-02', 'worksheet-game-crime-01', 'worksheet-game-crime-02', 'worksheet-00-welcome']:
      feedback = 'All correct'
      score = points_limit
   if key == 'worksheet-15-A-external-merge-sort':
      q = 'Initial.Run.External.Merge.Sort'
      if q in correct and not correct[q]:
         if theirAnswers[q] == 'b_r-b_r-ceiling(b_r/M)':
            feedback = re.sub(f'{q},', '', feedback)
            feedback = re.sub(q, '', feedback)
            score = min(score + rubrics[q]['points'], points_limit)

   if key in ['m1-just-material-might-50']:
      if 'Teachers.Teach.' in feedback:
         feedback = re.sub(r'Teachers.Teach.\d,', '', feedback)
         feedback = re.sub(r'Teachers.Teach.\d', '', feedback)
         score = min(score + 3, points_limit)

   if key in ['game-nuclear-3']:
      if 'Parts.list.' in feedback:
         feedback = re.sub(r'Parts.list.\d.\d,', '', feedback)
         feedback = re.sub(r'Parts.list.\d.\d', '', feedback)
         score = min(score + 20, points_limit)
      if 'Employee.Door.Counts' in feedback:
         feedback = re.sub(r'Employee.Door.Counts.\d.\d,', '', feedback)
         feedback = re.sub(r'Employee.Door.Counts.\d.\d', '', feedback)
         score = min(score + 40, points_limit)

   # Check for any corrections in the corrections table
   cursor.execute('''SELECT *
                       FROM Corrections
                      WHERE key=%(key)s AND
                            post_id =%(post_id)s  ''',
                  dict(key=key, post_id=post_id))
   for row1 in cursor.fetchall():
       if row1.field in feedback:
           feedback = re.sub(f', {row1.field}', '', feedback)
           feedback = re.sub(f'{row1.field}, ', '', feedback)
           feedback = re.sub(row1.field, '', feedback)
           score = min(points_limit, row1.score + score)

   if score < points_limit:
      this_score = score * 100.0 / points_limit
      # For any worksheet or game handed in on time that gets 75-99%, give 'em a 100%
      # For any worksheet or game handed in on time that gets <50%, give 'em 50%
      cursor.execute('''SELECT assessment_type
                          FROM Rubrics
                         WHERE key=%(key)s   ''',
                     dict(key=key))
      row1 = cursor.fetchone()
      if row1 and row1.assessment_type in ['worksheet', 'game']:
         if 75 <= this_score < 100:
            score = points_limit
         if 50 > this_score:
            score = points_limit / 2

   feedback = feedback.strip()
   if feedback:
      feedback = "Incorrect: " + feedback
   else:
      feedback = "All correct"

   return correct, score, feedback, points_total


class Grader:
   """Handle grading a submission"""

   def __init__(self, key, cursor):
      """Grade posts for key"""
      self.key = key
      self.cursor = cursor
      self.cursor.execute("""select questions, info from rubrics where key = %s""", [key])
      row = self.cursor.fetchone()
      if row:
         self.rubrics = row.questions
         self.info = row.info
         self.exam = self.info.get("exam", 0)
         self.ps = "due" in self.info
      else:
         raise "missing rubrics for " + key

   # process each post producing feedback
   def gradeOne(self, onyen, post_id):
      """Grade a single assignment producing score and feedback"""
      # I'm doing this dance to avoid the apply double evaluation bug
      if args.verbose:
         print(f"gradeOne: grading key {self.key} onyen {onyen} post id {post_id}")
      # grab the values they submitted, store in a dictionary
      theirAnswers = self.getAnswers(post_id)
      result = evalMultiple(theirAnswers, self.rubrics, self.key, onyen, post_id)

      # Call get feedback and update feedback to get/store the grade feedback
      correct, score, feedback, points_total = get_feedback(self.cursor, self.key, onyen,
                                                            post_id, theirAnswers,
                                                            self.rubrics, result, self.info)
      self.updateFeedback(onyen, post_id, correct, score, feedback, points_total)

      # compare what they saw to my results
      check = theirAnswers.get("_check")
      if check:
         for i, k in enumerate(tagSort(correct.keys())):
            if check[i] != "-" and check[i] == "1" and not correct[k]:
               print(f"{onyen}: bad check {k} {post_id}")


   def getInfo(self, onyen, key, section, default=None):
      """Get info allowing for exceptions"""
      exceptions = self.info.get("exceptions", {})
      info = {**self.info,
              **exceptions.get(f"_{section}", {}),
              **exceptions.get(onyen, {})}
      return info.get(key, default)

   def getAnswers(self, post_id):
      """Retrieve the answers for a post"""
      self.cursor.execute("""
            select A.field, A.value
            from Answers A
            where A.post_id = %(post_id)s and
                (SUBSTRING(A.field FROM 1 FOR 1) != '_' or
                 SUBSTRING(A.field FROM 2 for 1) != LOWER(SUBSTRING(A.field FROM 2 FOR 1)))
            order by A.post_id asc
        """,
                          dict(post_id=post_id),
                          )
      answers = dict(cursor)
      return answers

   def updateFeedback(self, onyen, post_id, correct, score, feedback, points_total):
      """Remove the old database feedback tuple, insert this feedback, updateGrades table"""

      # clear old feedback for exams where there should be only one
      self.cursor.execute(""" DELETE FROM feedback WHERE post_id=%(post_id)s """,
                         dict(post_id=post_id))
      self.cursor.execute("""
                INSERT INTO Feedback (post_id, score, points_total, msg, elapsed_time)
                values (%(post_id)s, %(score)s, %(points_total)s, %(msg)s, 
                        --- Calculate the post time minus the first fetch time as elapsed time
                        (SELECT P.time - (SELECT MIN(F.time)
                                            FROM Fetched as F
                                           WHERE F.onyen=%(onyen)s AND
                                                 F.key=%(key)s)
                           FROM Post as P
                          WHERE P.post_id = %(post_id)s))  """,
                        dict(post_id=post_id,
                             score=score,
                             points_total=points_total,
                             msg=feedback,
                             onyen=onyen,
                             key=self.key))
      # Update the assessments table for the key and onyen
      self.cursor.execute("""
           WITH A AS (SELECT P.post_id, R.assessment_type
                        FROM Rubrics R, Post P, Answers A
                       WHERE R.key = %(key)s AND
                             R.key = P.key AND
                             P.onyen = %(onyen)s and
                             A.post_id = P.post_id AND
                             A.field = '_submit' AND
                             A.value = 'Submit')

           SELECT A.post_id, A.assessment_type, F.score, F.points_total
             FROM A
             LEFT JOIN Feedback F ON F.post_id = A.post_id
            ORDER BY A.post_id  """,
                             dict(key=self.key,
                                  onyen=onyen))
      sum_scores = 0
      max_scores = 0
      num_subs   = 0
      num_grades = 0
      one_submission_graded_100_percent = False
      for index, row in enumerate(self.cursor.fetchall()):
          if row.score is None or row.points_total == 0:
              this_score = 0
          else:
              this_score = row.score * 100.0 / row.points_total
              num_grades += 1
          sum_scores += max(this_score - max_scores, 0) / (index + 1)
          max_scores = max(this_score, max_scores)
          if this_score >= 100 and not one_submission_graded_100_percent:
             one_submission_graded_100_percent = True
          num_subs += 1
      cursor.execute("""
          INSERT INTO Assessments (key, assessment_type, onyen,
                                   one_submission_graded_100_percent,
                                   overall_percentage, number_graded, number_submissions)
                          VALUES(%(key)s, %(assessment_type)s, %(onyen)s,
                                 %(one_submission_graded_100_percent)s,
                                 %(overall_percentage)s, %(number_graded)s, %(number_submissions)s)
                 ON CONFLICT(key, onyen) DO UPDATE
                    SET assessment_type=%(assessment_type)s,
                        one_submission_graded_100_percent=%(one_submission_graded_100_percent)s,
                        overall_percentage=%(overall_percentage)s,
                        number_graded=%(number_graded)s,
                        number_submissions=%(number_submissions)s  """,
                        dict(key=self.key,
                             assessment_type=row.assessment_type,  # pylint: disable=undefined-loop-variable
                             onyen=onyen,
                             one_submission_graded_100_percent=one_submission_graded_100_percent,
                             overall_percentage=sum_scores,
                             number_graded=num_grades,
                             number_submissions=num_subs))

      updateGrades(self.cursor, onyen)
      self.cursor.connection.commit()


def tagSort(tags):
   """Sort questions in reasonable order"""
   return sorted(
      tags,
      key=lambda tag: [
         s.isdigit() and int(s) or s for s in re.findall(r"\d+|\D+", tag)])


symbols = re.compile(r"[$a-zA-Z][a-zA-Z0-9]*|" + r"0x[0-9a-fA-F]+|[\d.]+|<<|>>|\*\*|\S")


def getSymbols(text):
   """Convert string to list of symbols"""
   text = re.sub(r"#.*", "", text)  # Remove python comments
   text = re.sub(r"--.*", "", text) # Remove SQL comments
   text = re.sub(r"//.*", "", text) # Remove JavaScript comments
   return symbols.findall(text)


def getDistance(original, partial):
   """Compute the edit distance"""
   return WagnerFischer(
      original, partial, insertion=lambda s: 1 if s not in "()" else 0).cost


if __name__ == "__main__":
   args = Args.Parse(
      testing=0,
      verbose=1,
      validate=0,
      force=False,  # boolean to force or not force grading an item
      key="", # set to grade any available from that key
      onyen="",  # set to select only one onyen to grade
      maxpenalty=1.0,  # set to reduce max penalty
      penalty=0.20,
      )

   # ## Connect to the class db
   db.init()
   conn = db.open_db()
   cursor = conn.cursor()
   print(f'grade.py {datetime.now()}')

   cursor.execute('SELECT onyen FROM roll')
   onyens = [x.onyen for x in cursor.fetchall()]
   assert args.onyen == '' or args.onyen in onyens, f"Onyen {args.onyen} is not in the class roll"
   cursor.execute('SELECT distinct key FROM Rubrics')
   keys = [x.key for x in cursor.fetchall()]
   assert args.key == '' or args.key in keys, f"Key {args.key} is not in any class assessment"
   force = args.force is True

   # find those who need grading
   if force:
      print(f"Forcing regrade for key {args.key} {f'for onyen {args.onyen}' if args.onyen else ''} ")
      cursor.execute("""
            select P.post_id, P.key, P.onyen
            from Post P, Answers A
            where (P.key = %(key)s or %(key)s = '' ) and
                  P.post_id = A.post_id and
                  A.field = '_submit' and
                  A.value = 'Submit' and
                  (P.onyen = %(onyen)s or %(onyen)s = '') 
            order by P.key, P.post_id, P.onyen  """,
                     {"key": args.key, "onyen": args.onyen},
                     )
   else:
      print(f"Processing grades for {'all keys' if args.key == '' else 'key ' + args.key} {f'for onyen {args.onyen}' if args.onyen else ''} ")
      cursor.execute("""
            select P.post_id, P.key, P.onyen
            from Post P, Answers A
            where (P.key = %(key)s or %(key)s = '') and
                  P.post_id = A.post_id and
                  A.field = '_submit' and
                  A.value = 'Submit' and
                  (P.onyen = %(onyen)s or %(onyen)s = '') AND
                  P.post_id not in (select F.post_id from Feedback F)
            -- Order by post_id which is essentially time so that onyen AAA doesn't always grade first      
            order by P.key, P.post_id, P.onyen  """,
                        dict(key=args.key, onyen=args.onyen))
   toGrade = cursor.fetchall()
   print(f"{len(toGrade)} assessment to grade {datetime.now()}")

   # It's important to grade things in order of post_id then onyen
   # Limit DOS attack where student submits many requests.
   previous_key = None
   for row in toGrade:
       if row.key != previous_key:
           grader = Grader(row.key, cursor)
           if args.verbose:
               print(f"Submissions of {row.key} needed to grade:\t")
           previous_key = row.key
       grader.gradeOne(row.onyen, row.post_id)
   print(f"{len(toGrade)} graded {datetime.now()}")
