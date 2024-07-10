#! /usr/bin/python3
""" Determine if reveal-md is already running, if so cancel it
    Then start up reveal-md by first processing all .tmd files
    Lastly watch for any .tmd file updates and restart reveal-md
"""
import os
import re
import signal
import sys
import time
# pylint: disable=invalid-name, too-many-branches
from datetime import datetime
from glob import glob
from shutil import copyfile
from subprocess import CalledProcessError, Popen, check_output, run

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

import Args
from updateReveal import process_tmd_files

patterns = ["*.tmd", "theme/lejeune.css"]
ignore_patterns = ""
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories,
                                               case_sensitive)
args = Args.Parse(
        deploy=0,
        )

reveal_pid = None
def restart_reveal(deploy):
    """ Kill the existing reveal-md, process all .tmd files, and start a new reveal-md
        If deploy==0, then immediately kill the deploy"""
    global reveal_pid  # pylint: disable=global-statement

    try:
        copyfile('theme/lejeune.css',
            '/usr/local/lib/node_modules/reveal-md/node_modules/reveal.js/dist/theme/lejeune.css')
    except IOError:
        print('Copying theme to node_modules received Permissin Error: Ignoring!')
    process_tmd_files()
    md_files = glob("*.md")
    if reveal_pid:
        print(f"Killing {reveal_pid.pid}")
        os.kill(reveal_pid.pid, signal.SIGTERM)
        os.system('killall chrome')
        time.sleep(1)
    else:
        try:
            pids = map(int, check_output(["pidof", "node"]).split())
        except CalledProcessError:
            pids = []
        for pid in pids:
            output = check_output(f"ps -o cmd= {pid}", shell=True)
            if output.find(b'/usr/local/bin/reveal-md') > 0:
                os.kill(pid, signal.SIGTERM)
    cmd_list = ['/usr/local/bin/reveal-md', '--print-size', '', '--theme', 'lejeune'] + md_files
    reveal_pid = Popen(cmd_list) # pylint: disable=consider-using-with
    print(f"Reveal-md pid is {reveal_pid.pid}")

    # Ensure PDF files are newer than md files
    for md_file in md_files:
        pdf_file = re.sub(r'.md$', r'.pdf', md_file)
        md_mtime = datetime.fromtimestamp(os.path.getmtime(md_file))
        try:
            pdf_mtime1 = datetime.fromtimestamp(os.path.getmtime(f'../../static/slides/{pdf_file}'))
        except FileNotFoundError:
            pdf_mtime1 = datetime.fromtimestamp(0)
        try:
            pdf_mtime2 = datetime.fromtimestamp(os.path.getmtime(
                f'/var/www/mypoll/content/slides/{pdf_file}'))
        except FileNotFoundError:
            pdf_mtime2 = datetime.fromtimestamp(0)
        if pdf_mtime1 < md_mtime or pdf_mtime2 < md_mtime:
            # pylint: disable=subprocess-run-check
            print(f"Updating PDF {pdf_file} from {md_file}")
            if deploy == 0:
                subprocess_rtn = run  # Run and wait
            else:
                subprocess_rtn = Popen
            subprocess_rtn(['node_modules/.bin/decktape', '--size', '612x750',
                            '--chrome-path', '/usr/bin/chromium-browser', 'reveal',
                            f'http://localhost:1948/{md_file}',
                            f'/var/www/lejune/content/static/slides/{pdf_file}'])
            subprocess_rtn(['node_modules/.bin/decktape', '--size', '612x750',
                            '--chrome-path', '/usr/bin/chromium-browser', 'reveal',
                            f'http://localhost:1948/{md_file}',
                            f'../../static/slides/{pdf_file}'])
    if deploy==0:
        os.kill(reveal_pid.pid, signal.SIGTERM)

restart_reveal(args.deploy)
if args.deploy==0:
    # Don't deploy the server
    sys.exit(0)

def on_modified(event):
    """ Print update notification and restart reveal-md """
    print(f"{event.src_path} was modified!")
    restart_reveal(args.deploy)

def on_created(event):
    """ Print update notification and restart reveal-md """
    print(f"{event.src_path} was created!")
    restart_reveal(args.deploy)

def on_deleted(event):
    """ Print update notification and restart reveal-md """
    print(f"{event.src_path} was deleted!")
    restart_reveal(args.deploy)

def on_moved(event):
    """ Print update notification and restart reveal-md """
    print(f"{event.src_path} was moved!")
    restart_reveal(args.deploy)

# Set up event handlers that watch for changes to
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

my_observer = Observer()
path = "."  #  Any patterns in the current directory
go_recursively = True
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

# Watchdog for *.tmd update, create, delete, or move
my_observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()
