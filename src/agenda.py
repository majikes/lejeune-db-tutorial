"""Simple hacks for an agenda"""
# pylint: disable=too-many-branches, unsupported-membership-test, too-many-statements, bad-indentation

from datetime import date, timedelta
import re

from bottle import SimpleTemplate
from config import first_day_of_classes, last_day_of_classes, no_classes, remote_classes

import db
from appbase import get_url, log, renderMarkdown, renderTemplate, show_agenda_comment
## Do not import anything from app.py as it will cause a RuntimeWarning overwriting routes

link = SimpleTemplate('<a href="{{url}}" target="_blank">{{text}}</a>')
db.init()

def comment_line(line, onyen):
   """ When parse reads a line starting with a #, create a comment line for admin users """
   if not show_agenda_comment(onyen):
      return ""

   line = renderMarkdown(line[1:])
   return f"<font color='grey'>{line}</font>"

def slide_line(line):
   """ Given an agenda line, create a slide html link for it """
   words = line[2:].strip().split(' ', 1)
   assert len(words) == 2, f"agenda.py: {line}\nsplit_line should be a " + \
       f"filename in content/slides and then a description: {line}"
   try:
      url = get_url('slides', slide_name=words[0])
      line = link.render(text=f'Slides: {words[1]}', url=url)
   except FileNotFoundError:
      # On some systems, the slides are not produced
      line = f'Slides: {words[1]} not found'
   return line

def zoom_line(line, day, section, lecture_urls, recitation_url):
   """ Given a zoom line, create a zoom html link for it
       Note that the day (T/W/TH) and section number effect the zoom link"""
   video = line[1:].strip().replace("https://unc.zoom.us", "")
   if not video:
      if day.weekday() in [1, 3]:
         if len(lecture_urls) == 1:
            line = link.render(text=f"Join section {section} lecture on Zoom",
                               url=lecture_urls[0]) + '<br />'
         else:
            line = ''
            for index, lecture_url in enumerate(lecture_urls):
               line += link.render(text=f"Join section 00{index+1} lecture on Zoom",
                                   url=lecture_url) + '<br />'
      else:
         url = recitation_url
         if url:
            line = link.render(text="Join recitation on Zoom", url=url) + '\n'
   else:
      url = get_url("zoom", video=video)
      line = link.render(text="Recording", url=url)
   return line

def get_days_tense(day, today):
   """ Given a day and today, determine when the day is.  past, present, future"""
   if day < today:
      return "past"
   if day == today:
      return "present"
   return "future"

def increment_day(day, LDOC):
   """ Given a day (T/W/TH), increment it to the next class (W/TH/T) """
   assert day <= LDOC, f'Day {day} falls after the '\
                       f'last day of classes {last_day_of_classes}'
   if day.weekday() in [0, 1]:  # Monday or Tuesday
      day += timedelta(days=2)
   else:
      day += timedelta(days=5)  # Wednesday or Thursday
   if day in no_classes:
       day = increment_day(day, LDOC)
   return day

def checklist_line(line, day, same_day, checklist, cursor):
   """ Given a line of checklist items separated by |, the day, and the user...
       return a html checklist
       Note: If the user previously checked the item, then the checklist dictionary
       will have a key with that date and an array element with the item name
       A base assumption is that jinga substitution({{ }}) is only used in
       anchor links!
    """

   if same_day:
       output_lines = ''
   else:
       output_lines = f'<b>Checklist items due before class on {day}</b>'
       output_lines += f'<ul class="checklist" id="check-list-{day}">'
   for item in line[2:].split(' | '):
      item = item.strip()
      # Find assessment key if one exists in the item
      if "@" in item:
          key_start_index = item.index("@")
          key = item[key_start_index + 1:].strip()
          item = item[:key_start_index-1]
      else:
          key = ""

      # Need to remove all []() Markdown html links as it's not in the item the user selected
      # The long, nested parenthesis regex: https://stackoverflow.com/questions/546433/regular-expression-to-match-balanced-parentheses
      item_without_markdown_link = item
      previous_item_without_markdown_link = ''
      while re.match(r'.*\[.*\]\(.*\)', item_without_markdown_link):
         assert previous_item_without_markdown_link != item_without_markdown_link, f'Infinite loop processing markdown link in {item_without_markdown_link}'
         previous_item_without_markdown_link = item_without_markdown_link
         # WARNING: This instruction will be an infinite loop if you have a malformed link!
         # Especially a link without the closing )!!!
         item_without_markdown_link = re.sub(r"\[(.*?)\]\((?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*\)", r"\1", item_without_markdown_link)
      # Process all markdown (ticks, **, _, etc)
      item_without_markdown = renderMarkdown(item_without_markdown_link)
      # HtML removes double blanks
      item_without_double_blanks = re.sub(r"   *", " ", item_without_markdown)
      # Remove any remaining html
      item_without_html = re.sub(r"\<.*?\>", "", item_without_double_blanks)
      # Checklist items with python variables/jinga are not allowed
      assert not re.match(r'.*{{.*}}', item_without_html), f'Checklist items cannot have python variables in them: {item_without_html}'

      # Now that we have the item, if it has a worksheet, update the checklist worksheet
      if key != "":
          # Since this is executed by each user, expect and ignore duplicate inserts
          cursor.execute("""
                INSERT INTO checklist_worksheet (lecture_date, item, key)
                                         VALUES (%(date)s, %(item)s, %(key)s)
                       ON CONFLICT DO NOTHING  """,
                         dict(date=day, item=item_without_html, key=key))


      # If the item is in the checklist present check, otherwise unchecked
      if day in checklist and item_without_html in checklist[day]:
         output_lines += f'<li class="unchecked checked">{item}</li>'
      else:
         output_lines += f'<li class="unchecked">{item}</li>'
   output_lines += '</ul>'
   return output_lines

def get_checklist_info(cursor, onyen):
   """ Get the checklist information for the user.
       Return a dictionary with the lecture date (not str) as the key with
       a value of an array of each item checked
       NOTE: the checklist is a log, so find the latest item in the checklist for
       each lecture date """
   cursor.execute('''
      -- C1 is the ranked by time items for each lecture_date and time
      WITH C1 as (SELECT lecture_date, checked, item,
                         rank() over(partition by lecture_date, item
                                               order by time desc)
                    FROM checklist
                   WHERE onyen=%(onyen)s)

      SELECT lecture_date, item
        FROM C1
       WHERE rank=1 AND    -- only the latest time / rank (ignore the others in the log)
             checked=true  -- only latest items that are checked true ''',
              dict(onyen=onyen))

   checks = {}
   for row in cursor.fetchall():
       if row.lecture_date not in checks:
          checks[row.lecture_date] = []
       checks[row.lecture_date].append(row.item)
   return checks


@db.with_db_cursor
def parse(file_name, onyen, cursor):
   """Main routine called by home.tmd to parse agenda.tmd"""
   cursor.execute('''select section from roll where onyen=%(onyen)s''', dict(onyen=onyen))
   row = cursor.fetchone()
   section = None if row is None else row.section

   # Get checklist items that are marked checked for this user
   checklist_info = get_checklist_info(cursor, onyen)

   today = date.today()
   with open(file_name, "rt", encoding='utf-8') as fp:
      agenda = fp.read().split("\n| ")
   day = first_day_of_classes
   last_checklist_day = None  # Remember if this day has multiple checklists
   result = []
   for one_days_details in agenda:
      lines = one_days_details.split("\n")
      title = lines[0]
      if day in remote_classes:
         title += ' - REMOTE!!!'
      output_lines = []
      for line in lines[1:]:
         if line.startswith("S "):
            line = slide_line(line)
         elif line.startswith("P1") or line.startswith("P2"):
            line = panopto_line(line, section)
         elif line.startswith("#"):
            line = comment_line(line, onyen)
         elif line.startswith("CL"):
            if last_checklist_day == day:
                # Remove the </ul> from output
                assert output_lines[-1][-5:] == '</ul>', output_lines
                output_lines[-1] = output_lines[-1][:-5]
            line = checklist_line(line, day, day == last_checklist_day, checklist_info, cursor)
            last_checklist_day = day
         else:
            output_lines.append('')  # Need multiple lines
         output_lines.append(line)
      when = get_days_tense(day, today)

      result.append(
         {"date": day, "title": title, "when": when,
          "body": renderMarkdown(renderTemplate("\n".join(output_lines)))})
      if day > last_day_of_classes:
         log(f'Day {day} is after the LDOC {last_day_of_classes}',
             f'The agenda line {title} should be removed')
         assert day <= last_day_of_classes, f'Day {day} is after the LDOC {last_day_of_classes}. The agenda line {title} should be removed'
      day = increment_day(day, last_day_of_classes)
   return result


def panopto_line(line, section):
   """ When parse reads a line starting with a Px, create a panopto line """
   if section is None:
      return ""
   if (section == '001') and  (line[0:2] == 'P2'):
      return ""
   if (section == '002') and  (line[0:2] == 'P1'):
      return ""

   return renderMarkdown(renderTemplate(line[3:]))


def due(m, d):
   """ Can this be deleted? """
   return f"{m}/{d}"
