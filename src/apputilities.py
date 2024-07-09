"""
Utilities for all the endpoint methods
"""
# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation

import hashlib
import random
import re
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from typing import NoReturn

import dotenv

from appbase import get_url, get_onyen, get_onyen_for_endpoint
from assessments import SUBMITTABLE_PAGES
from bottle import HTTPError, request
from config import admin_email, gmail_host, gmail_user
from db import with_db_cursor
from ZWSP import ZWSP

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()


def log(*args):
    """Print for debugging"""
    print(*args, file=sys.stderr)


def json_converter(obj):  # pylint: disable=inconsistent-return-statements
    """ JSON override of datetime object """
    if isinstance(obj, datetime):
        return str(obj)


def onyen_in_roll(cursor, onyen):
   ''' Return boolean if onyen is in the class roll '''
   cursor.execute('''
      select exists (select onyen
                     from roll
                     where onyen = %(onyen)s and section in ('001', '002', '003'))  ''',
                  dict(onyen=onyen))
   return cursor.fetchone().exists


def get_submittable_notebook_info(cursor, onyen):
    ''' Get a dictionary with keys of all notebooks that are submittable
    and value of whether they need submit code'''
    cursor.execute('''
           WITH Ids AS (SELECT P.id, RANK() OVER(Partition by P.key     -- rank within each key
                                                 Order BY P.onyen DESC) -- prefer onyen page
                                                 AS rank_num
                          FROM Pages as P, Roll R, Rubrics
                         WHERE R.onyen = %(onyen)s AND
                               P.key = Rubrics.key AND
                               Rubrics.assessment_type = 'homework' AND -- homeworks are notebooks
                               P.start_time <= now() AND  -- include start_time
                               P.end_time > now() AND     -- exclude end_time
                               (P.onyen=R.onyen OR (P.onyen='' AND P.section=R.section)))

           SELECT P.key, array_agg(A.page_section) AS page_sections
             FROM Pages P, Active_sections A, Ids
            WHERE P.id = A.page_id AND
                  P.id = Ids.id AND
                  Ids.rank_num = 1 AND
                  A.page_section in %(submittable_pages)s
            GROUP BY P.key
            ORDER BY P.key ''',
                   dict(onyen=onyen,
                        submittable_pages=tuple(SUBMITTABLE_PAGES)))
    rv = {x.key: 'submit_code_req' in x.page_sections for x in cursor.fetchall()}
    return rv


def generate_submit_code(cursor):
    " Generate a new valid submit code "
    cursor.execute("SELECT C.code FROM Codes AS C")
    used = set(row.code for row in cursor.fetchall())
    candidates = set(f'{x}' for x in range(10000, 100000))  # 5 digit code
    new_code = random.sample(candidates - used, 1)[0]
    now = datetime.now()

    cursor.execute("""INSERT INTO Codes (time, code)
                                VALUES (%(time)s, %(code)s)  """,
                   dict(time=now+timedelta(minutes=1), code=new_code))
    return new_code, now

def validateSubmitCode(cursor, code):
    """See if the given submit code is valid"""
    code = code.strip()

    if not code:
        return False

    if code in ["have-a-great-winder-break"]:
        return True

    cursor.execute("""
         SELECT time
           FROM codes
          WHERE code = %(code)s  """,
                   dict(code=code))
    row = cursor.fetchone()
    if row is None:
        return False
    return datetime.now() < row[0]

def strUnicode(field):
    """ return unicode to string that is more readable """
    return re.sub(r'\u200b', 'u200b', re.sub(r'\u200c', 'u200c',
                                             re.sub(r'\u200d', 'u200d',
                                                    re.sub(r'\u200e', 'u200e',
                                                           re.sub(r'\u200f', 'u200f', field)))))

def email_alert(subject, note, to_list):
   """Send an email alert to_list should default to [admin_email]"""
   msg = MIMEText(note)
   msg['Subject'] = subject
   msg['From'] = gmail_user
   msg['To'] = admin_email
   s = smtplib.SMTP(gmail_host, 25)
   # s.ehlo()
   # s.login(gmail_user, gmail_password)
   s.sendmail(gmail_user, to_list, msg.as_string())
   s.quit()


def checkZWSP(fields, onyen, zwsp, key, post_id, cursor):  # pylint: disable=too-many-arguments
    """ Check if there's a zero-width space from a submission """
    if key[0] == '_':
        return  # We don't care about non-grade assessments
    re_prog = re.compile(ZWSP.ZWSP_regex)
    for _, fieldname, value in fields:
        if fieldname == '_submit' and 'pasted:' in value and re_prog.search(value):
            s = re_prog.search(value)
            zwsp_pasted = s.group(0)
            byte_array = f'\\x{bytearray(zwsp_pasted.encode("utf-8")).hex()}'
            cursor.execute('''
                      SELECT onyen
                        FROM roll
                       WHERE zwsp::bytea = %(data)s''',
                           dict(data=byte_array))
            row = cursor.fetchone()
            if row:
                log(f'checkZWSP: post_id {post_id} onyen {onyen} copied from {row.onyen} for {key} data {value}')
                cursor.execute('''
                      INSERT INTO zwsp
                                  (postid, fieldname, s_onyen)
                           values (%(post_id)s, %(fieldname)s, %(onyen)s) ''',
                               dict(post_id=post_id,
                                    fieldname=f"{value} {onyen}",
                                    onyen=row.onyen))


@with_db_cursor
def get_team(cursor):
   ''' Get the onyen's team number '''
   onyen, _ = get_onyen_for_endpoint()
   cursor.execute("""
        SELECT R.onyen, R.name
          FROM Roll AS R, Teams AS T
         WHERE T.onyen = R.onyen AND
               T.number = (SELECT T.number
                             FROM Teams T
                            WHERE onyen=%(onyen)s)
         ORDER BY R.name  """,
                  dict(onyen=onyen))
   result = cursor.fetchall()
   return result

def linkable_header(title):
   ''' given a title, create a linkable header '''
   name = title.lower().replace(' ', '-')
   return f'<a href="#{name}" name="{name}"><u>{title}</u></a>'

def not_found(cursor, msg=None) -> NoReturn:
    """Return a custom 404 message"""
    onyen = get_onyen()
    now = datetime.now()
    ip = request.remote_addr
    url = request.url
    cursor.execute("""INSERT INTO notfound
                              (time, onyen, ip, url)
                       VALUES (%(time)s, %(onyen)s, %(ip)s, %(url)s)""",
                   dict(time=now, onyen=onyen, ip=ip, url=url))
    cursor.connection.commit()  # Need to commit as 404 is a bad return code
    if not msg:
        msg = f"""Sorry {onyen}: File not found. Every access is recorded."""
    raise HTTPError(404, msg)


def not_allowed() -> NoReturn:
    """Return a custom 405 message"""
    onyen = get_onyen()
    msg = f"""Sorry {onyen}: It appears you are not registered for this class."""
    raise HTTPError(405, msg)

def get_worksheet_bonus_information(cursor, section):
   """ Get the data for the worksheet bonus view """

   if section == '':
      cursor.execute("""
           select onyen, section, name
              from roll
              order by section asc, onyen asc
           """)
   else:
      cursor.execute("""
           select onyen, section, name
              from roll
              where section = %(section)s
              order by section asc, onyen asc
           """,
                     dict(section=section))
   students = []
   for row in cursor.fetchall():
      index = row.name.find(', ')
      students.append({"onyen": row.onyen,
                       "id": row.name,
                      })
      students.append({"onyen": row.onyen,
                       "id": f"{row.name[index+2:]} {row.name[:index]}"
                      })
      students.append({"onyen": row.onyen,
                       "id": row.onyen
                      })
   students = sorted(students, key=lambda k: k['id'].lower())

   cursor.execute("""
        select id, onyen, submitter, share_time, reason
           from worksheet_bonus
           order by id desc
        """)
   bonuses = [{"onyen": row.onyen,
               "id": row.id,
               "submitter": row.submitter,
               "timestamp": row.share_time,
               "reason": row.reason,
              }
              for row in cursor.fetchall()]

   return {"students": students,
           "bonuses": bonuses,
           "section": section}

def set_worksheet_bonus(cursor, onyen, submitter, reason, ip='127.0.0.1', section=""):  # pylint: disable=too-many-arguments
   """ Implement the setting of a worksheet bonus """
   share_time = datetime.now()
   cursor.execute("""
      insert into worksheet_bonus
        (onyen, submitter, share_time, reason, ip)
        values (%s, %s, %s, %s, %s)
        returning id
      """,
                  [onyen, submitter, share_time, reason, ip],
                  )
   wsb_id = cursor.fetchone()[0]

   # Send an acknowledgement of the submission
   to_email = f"{onyen.lower()}@email.unc.edu"
   grade_url = f"{dotenv_values['HTTPS_FQDN']}{get_url('grades')}"
   note = f"""
The system has received a worksheet bonus submission of up to 5% on a worksheet score for {onyen} with id {wsb_id}.

You can view the submission at {grade_url}"""
   email_alert(f"Worksheet bonus {wsb_id}", note, to_list=[to_email, admin_email])

   return get_worksheet_bonus_information(cursor, section)


def check_submittable(cursor, key, onyen, section):
    """ Check db for key/onyen/section has submit on """
    cursor.execute("""
               select id
                 from active_sections
                where page_section='submit' and
                      page_id=(select id
                                 from pages
                                where key=%(key)s and
                                      (onyen=%(onyen)s or section=%(section)s) and
                                      start_time < now() and
                                      end_time > now()
                                      order by onyen desc -- Prefer access page for onyen over section
                                      limit 1             -- Only get the first access page
                                      )
               """,
                   dict(key=key, section=section, onyen=onyen))
    row = cursor.fetchone()
    if not row or not row.id:
        log(f"Onyen {onyen} tried to submit but there is no submit section for key {key}")
        raise HTTPError(401, f"At this time, submits are not permitted for {key} and onyen {onyen}")


def get_text(fname):
   """Return the first line for identification"""
   line = 'No title'
   with open(fname, encoding='utf-8') as f:
      for line in f:
         if re.match(r'^# .*$', line):
            break
         line = re.sub("^# ", "", line)
   return line

def fileHash(filename):
    '''Compute the checksum to be sure the file is what we expect'''
    # Must be identical to comp116.fileHash
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as hash_fp:
        buf = hash_fp.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = hash_fp.read(BLOCKSIZE)
    return hasher.hexdigest()
