"""Basics of a Bottle web server"""

# pylint: disable=unsupported-membership-test, too-many-statements, bad-indentation
import contextlib
import getpass
import html
import json
import os.path as osp
import os
import re
import sys
import traceback

import dotenv

import bottle
import db
from db import with_db_cursor
from bottle import request, HTTPError
import markdown
from config import admins

# lax security when testing
Testing = False

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

# startup bottle
app = application = bottle.Bottle()

md = markdown.Markdown(tab_length=8, extensions=['extra', 'tables'])  # pip install Markdown markdown-extra

def log(*args):
   """Print for debugging especially when doing make deploy"""
   print(*args, file=sys.stderr)

def renderMarkdown(base):
   """ Handle Markdown processing by changing dollar sign to spans, etc """
   md.reset()
   # Allow dollar sign and \( for mathjax markdown
   base = re.sub(r"\\\((.*?)\\\)", r'<span class="math">\1</span>', base)
   base = re.sub(r"\$(.*?)\$", r'<span class="math">\1</span>', base)
   base = md.convert(base)
   return base


def renderTemplate(name, **kwargs):
   """Render a template being careful to handle errors"""
   try:
      result = bottle.template(name, dotenv_values, **kwargs)
      return result
   except:
      onyen = get_onyen()
      if onyen_is_admin(onyen):
         result = html.escape(traceback.format_exc())
         result = f"\n<pre>{result}</pre>"
         return result
      raise


# make get_url available in all templates
def get_url(name, onyen=None, **kwargs):
    """get_url for use from templates"""
    url = app.get_url(name, **kwargs)
    real_onyen = get_onyen()
    if onyen and onyen_is_admin(real_onyen) and real_onyen != onyen:
        url = url + f"?onyen={onyen}"
    return url

bottle.SimpleTemplate.defaults["get_url"] = get_url


# load secrets needed at runtime
with open("secrets.json", encoding="utf-8") as f:
   secrets = json.load(f)

def check_bad_parm():
    """ Check for things that bite me all the time"""
    if request.query.userid:
        raise HTTPError(401, "Invalid parameter userid... onyen")
    if request.query.user:
        raise HTTPError(401, "Invalid parameter user... onyen")

def allow_json(func):
    """ Decorator: renders as json if requested """

    def wrapper(*args, **kwargs):
        """wrapper"""
        result = func(*args, **kwargs)
        if "application/json" in bottle.request.headers.get("Accept", "") and isinstance(result, dict):
            return bottle.HTTPResponse(result)
        return result

    return wrapper


# simple minded security
def onyen_is_known(_dummy_supplied_by_wrapper):
    """The user has logged in"""
    return get_onyen()


def token_is_known_onyen(token):
    """ Really this needs to check the db"""
    connection = db.open_db()
    with contextlib.closing(connection):
        cursor = connection.cursor()
        cursor.execute('''SELECT EXISTS(SELECT onyen
                                          FROM roll
                                         WHERE onyen=%(token)s)''',
                       dict(token=token))
        onyen = cursor.fetchone()[0]
        log(f'token_is_known_onyen: token={token} found onyen={onyen}')
        return onyen

def show_agenda_comment(onyen):
    '''If the onyen is an administrator and the showcomment query is specified, return True
    Otherwise return False'''
    if onyen_is_admin(onyen) and request.query.showcomment:
        return True
    return False

def get_onyen_for_endpoint():
    """ For an endpoint, get the onyen of the original user and
    if the endpoint is an administrator pretending to be a user
    Return the onyen, and the original_onyen """
    onyen = get_onyen()
    check_bad_parm()
    if onyen_is_admin(onyen) and request.query.onyen:
        original_onyen = onyen
        onyen = request.query.onyen
    else:
        original_onyen = ''
    return onyen, original_onyen

def get_onyen():
    """Return the onyen from the cookie"""
    #JJM log(f"get_onyen appbase begin")
    #JJM keys = [x for x in request.environ.keys()]
    #JJM for k in keys:
    #JJM     log(f"get_onyen appbase {k}='{request.environ[k]}'")
    #JJM log(f"get_onyen appbase done")
    onyen = bottle.request.environ.get("HTTP_REMOTE_USER", "")
    log(f"JJM get_onyen HTTP_REMOTE_USER onyen='{onyen}'")
    if onyen == '':
        onyen = bottle.request.get_cookie("username", secret=secrets["cookie"])
        log(f"JJM get_onyen HTTP_REMOTE_USER get_cookie username '{onyen}'")
    if onyen == "":
       onyen = os.environ.get('username', '')
       log(f"JJM get_onyen environ HTTP_REMOTE_USER username='{onyen}'")
    #JJM log(f"JJM get_onyen: HTTP_REMOTE_USER='{onyen}'")
    #JJM if not onyen and Testing:
    #JJM   onyen = bottle.request.get_cookie("username", secret=secrets['cookie'])
    return onyen


def onyen_is_john(_dummy_supplied_by_wrapper):
    """ Is the onyen John Majikes"""
    return get_onyen() == 'jmajikes'


def onyen_is_admin(onyen=None):
    """The onyen is an administrator"""
    if onyen is None:
        onyen = get_onyen()
    return onyen in admins


bottle.SimpleTemplate.defaults["get_onyen"] = get_onyen
bottle.SimpleTemplate.defaults["onyen_is_admin"] = onyen_is_admin


def get_onyen_from_token():
    """Assuming the user has been verified, get the onyen"""
    if bottle.request.get_cookie('username', secret=secrets['cookie']):
        return bottle.request.get_cookie('username', secret=secrets['cookie'])
    return os.environ.get('username', '')

def set_onyen(onyen):
    """Set the onyen in the cookie"""
    bottle.response.set_cookie(
        "username", onyen, secret=secrets["cookie"], secure=not Testing
    )
    log(f"JJM set_onyen set cookie username='{onyen}'")
    os.environ['username'] = onyen
    bottle.request.environ['HTTP_REMOTE_USER'] = onyen
    log(f"JJM set_onyen got username envir variable onyen='{os.environ.get('username', '')}'")


def auth(check, fail=False):
    """decorator to apply above functions for auth"""

    def decorator(function):
        """decorate itself"""

        def wrapper(*args, **kwargs):
            """wrapper"""
            onyen = get_onyen()
            if not onyen and fail:
                log(f'auth: onyen {onyen} fail {fail}')
                raise bottle.HTTPError(403, "Forbidden")
            if not onyen:
                path = bottle.request.path[1:]
                login_url = app.get_url("login")
                if login_url[:7] == '/mypoll':
                    # bottle.py get_url returns the request.environ SCRIPT_NAME prefix
                    login_url = login_url[7:]
                bottle.redirect(login_url + "?path=" + path)
            elif not check(onyen):
                log(f'auth: onyen {onyen} check {check} check(onyen) {check(onyen)}')
                raise bottle.HTTPError(403, "Forbidden")
            # Set the token read in /sso response
            bottle.response.set_cookie("username", onyen, secret=secrets["cookie"])
            return function(*args, **kwargs)

        return wrapper

    return decorator

def auth_pythonapp(check):
   """decorator to check the token on the python app endpoint calls"""

   def decorator(function):
       """decorate itself"""

       def wrapper(*args, **kwargs):
           """wrapper"""
           script_name = bottle.request.environ.get('SCRIPT_NAME', '')
           if script_name != '/pythonapp':
               log(f'auth_pythonapp: ERROR: script_name = "{script_name}"')
           http_user = bottle.request.environ.get('HTTP_REMOTE_USER', '')
           log(f"JJM wrapper HTTP_REMOTE_USER='{http_user}'")
           #JJM if http_user == '':
           #JJM     http_user = os.environ.get('username', '')
           #JJM if http_user != '':
           #JJM     log(f'auth_pythonapp: ERROR: HTTP_REMOTE_USER="{http_user}"')
           #JJM token = bottle.request.get_cookie('username', secret=secrets["cookie"])
           #JJM if not check(token) and not Testing:
           #JJM     log(f'auth_pythonapp: ERROR: failed authorization check: token={token}')
           #JJM     if token:
           #JJM         raise bottle.HTTPError(401, f'User "{token}" not authenticated through Single Sign On at https://comp421.cs.unc.edu')
           #JJM     raise bottle.HTTPError(401, 'Not authenticated through Single Sign On at https://comp421.cs.unc.edu')
           if not http_user:
               raise bottle.HTTPError(401, f'User not logged in')
           return function(*args, **kwargs)

       return wrapper

   return decorator


def static(filename):
    """
    Produce the path to a static file
    """
    p = osp.join("./static", filename)
    m = osp.getmtime(p)
    s = f"{int(m):x}"
    u = app.get_url("static", filename=filename)
    if u[:7] == '/mypoll':
        # bottle.py get_url returns the request.environ SCRIPT_NAME prefix
        u = u[7:]
    return u + "?" + s


bottle.SimpleTemplate.defaults["static"] = static


@app.route("/static/<filename:path>", name="static")
def serveStatic(filename):
    """
    Serve static files in development
    """
    kwargs = {"root": "./static"}
    if filename.endswith(".sqlite"):
        kwargs["mimetype"] = "application/octet-stream"
    # fake up errors for testing
    # import random
    # if random.random() < 0.5:
    #     return bottle.HTTPError(404, 'bogus')
    return bottle.static_file(filename, **kwargs)


@app.route("/login", name="login")
@bottle.view("login")
def login():
    """handle login with basic auth"""
    path = bottle.request.query.path
    log(f"JJM appbase GET login path={path}")
    return {"path": path, "message": ""}


@app.post("/login")
@with_db_cursor
@bottle.view("login")
def loginpost(cursor):
    """handle login submit"""
    forms = bottle.request.forms
    name = forms.name
    username = forms.username
    passwd = forms.passwd
    path = forms.path
    #JJM log(f"Post login appbase begin")
    #JJM keys = [k for k in request.environ.keys()]
    #JJM for k in keys:
    #JJM     log(f"POST login appbase {k}='{request.environ[k]}'")
    #JJM log(f"Post login appbase done")
    if not name or not username or not passwd:
        # Please enter all fields
        log(f"POST login appbase Please enter all fields: name='{name}', username='{username}', passwd='{passwd}'.")
        raise HTTPError(401, "Please enter all fields")
    cursor.execute("""
           SELECT password
             FROM Roll
            WHERE onyen = %(username)s """,
                   dict(username=username))
    row = cursor.fetchone()
    if row is None:
        # First time user logging in, set password
        log(f"POST login appbase Inserting username='{username}' name='{name}'")
        cursor.execute("""
               INSERT INTO Roll (onyen, name, password, section)
                           VALUES (%(username)s, %(name)s, %(passwd)s, '001')   """,
                       dict(username=username,
                            name=name,
                            passwd=passwd))
        cursor.connection.commit()
    elif row.password and passwd.upper() != row.password.upper():
        # User entered different password (or none at all) than the first time through
        log(f"POST login appbase Bad password. username='{username}' real password='{row.password}'",
            f" entered password='{passwd}'")
        raise HTTPError(401, f"Login failed.  Bad password '{passwd}'")
    set_onyen(username)
    # bottle.request.environ['HTTP_REMOTE_USER'] = username
    # log(f"POST login set HTTP_REMOTE_USER='{username}'")
    # log(f"POST login get HTTP_REMOTE_USER='{bottle.request.environ.get('HTTP_REMOTE_USER', '')}'")
    # if 'HTTP_REMOTE_USER' in bottle.request.environ:
    #    set_onyen(bottle.request.environ['HTTP_REMOTE_USER'])
    # else:
    #     set_onyen(username)
    log(f"POST login appbase username='{username}' password='{passwd}'")
    root_url = app.get_url("root")
    log(f"JJM POST login appbase root_url='{root_url}'")
    if path:
        log(f"JJM POST login appbase redirect='{root_url + path}'")
        bottle.redirect(root_url + path)
        return
    log(f"JJM POST login appbase redirect='{root_url}'")
    bottle.redirect(root_url)


@app.route("/logout", name="logout")
def logout():
    """Allow onyen to log out"""
    bottle.response.set_cookie("username", "", secrets["cookie"])
    os.environ['username'] = ''
    bottle.redirect('/')


@app.route("/api/onyen")
@app.route("/onyen")
@auth(onyen_is_known)
def this_onyen():
    """Report the current onyen for display on the page"""
    return {"onyen": get_onyen()}


class StripPathMiddleware:  # pylint: disable=too-few-public-methods
    """
    Get that slash out of the request
    """

    def __init__(self, a):
        self.a = a

    def __call__(self, e, h):
        e["PATH_INFO"] = e["PATH_INFO"].rstrip("/")
        return self.a(e, h)


def serve(test=True):
    """Run the server for testing"""
    from livereload import Server  # pylint: disable=import-outside-toplevel

    global Testing # pylint: disable=global-statement
    Testing = test

    bottle.debug(True)
    server = Server(StripPathMiddleware(app))
    if getpass.getuser() == 'jmajikes':
       port = '8081'
    elif getpass.getuser() == 'kaylanes':
       port = '8082'
    elif getpass.getuser() == 'ashams':
       port = '8083'
    elif getpass.getuser() == 'mshvets':
       port = '8084'
    else:
       port = '8087'
    server.serve(port=port, host="0.0.0.0", restart_delay=2)
