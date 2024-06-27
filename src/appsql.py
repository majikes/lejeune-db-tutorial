"""
 COMP 421 Specific routes
"""
# pylint: disable=unsupported-membership-test
import glob
import os.path as osp
from datetime import datetime

from appbase import application, StripPathMiddleware  # pylint: disable=unused-import
from appbase import app, auth, onyen_is_admin, onyen_is_known, get_onyen_for_endpoint
from apputilities import log, not_found
from bottle import request, view
from db import with_db_cursor


# list the SQL interpreter files
@app.get("/sql/interpreters", name="list_sql_interpreters")
@auth(onyen_is_admin)
@view("list_sql_interpreters")
def list_sql_interpreter():  # pylint:  disable=too-many-statements
    """ List all SQL interpreters """
    all_sql_interpreters = []
    files = glob.glob("content/sql/*.commands")
    if len(files) > 0:
        files.sort()
        all_sql_interpreters = [x.replace('content/sql/', '').replace('.commands','') for x in files]
    return dict(sql_interpreters=all_sql_interpreters)

# Process a SQL interpreter file
@app.get("/sql/interpreter/<key>", name="sql_interpreter")
@auth(onyen_is_known)
@view("sql_interpreter")
@with_db_cursor
def sql_interpreter(key, cursor):  # pylint:  disable=too-many-statements
    """ Read a sql_interpreter command file """
    onyen, original_onyen = get_onyen_for_endpoint()
    now = datetime.now()
    ip = request.remote_addr

    commands_path = f"content/sql/{key}.commands"
    if not osp.exists(commands_path):
        log(f"sql_interpreter: key {key} path {commands_path} not found")
        not_found(cursor)

    with open(commands_path, encoding='utf-8') as fid:
        commands = fid.read()

    # hold the lock for as little time as possible
    if original_onyen == '':
        cursor.execute("""
           INSERT INTO Fetched (time, onyen, key, ip, url)
                        VALUES (%(time)s, %(onyen)s, %(key)s, %(ip)s, %(url)s)  """,
                       dict(time=now, onyen=onyen, key=key, ip=ip, url=request.url))
    return dict(commands=commands, title=f'Demo {key}')
