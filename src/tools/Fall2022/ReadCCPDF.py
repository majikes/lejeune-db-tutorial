#!/usr/bin/env python3
""" Read a Connect Carolina PDF of student pictures with the corresponding
    Sakai CSV to create a classroll.csv file of students, pids, names and pictures
    that would be read by ReadClassRollIntoSQL.py
"""

# Need to pip3 install pymupdf

import Args
import fitz
import pandas
import re
import dotenv

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

args = Args.Parse(pdf=str,
                  csv=str,
                  verbose=0,
                 )

# doc = fitz.open("COMP550.001.20200704.pdf")
doc = fitz.open(args.pdf)
number_pages = len(doc)

roll = pandas.read_csv(args.csv)
try:
    columns = ['Student ID', 'PID', 'Name', 'Section', 'imageURL']
    roll = roll[columns]
except KeyError as e:
    print(f"You must ensure that the csv file has the headers {', '.join(columns)}")
    raise
roll.columns = ['onyen', 'pid', 'name', 'section', 'imageURL']
roll = roll.fillna('')

# Read all the PIDS from the Text part of the PDF
# Note that a PID must be 9 characters long and an integer
# Ignore all other text
class_pids = []
for page_number in range(number_pages):
   text = doc.get_page_text(page_number).split('\n')

   # Get all the pids on this page which are number strings of length 9
   pids = [int(x) for x in filter(lambda x: x.isnumeric() and len(x)==9, text)]
   class_pids.extend(pids)
number_of_pids = len(class_pids)

# Now for each picture in the page, match it up to the pid in sequence
number_of_images = 0
for page_number in range(number_pages):
   for img in doc.get_page_images(page_number):
      xref = img[0]
      pix = fitz.Pixmap(doc, xref) # Get the next Pixmap/picture

      # Get the next pid in the class pids
      pid = class_pids.pop(0)
      try:
         onyen = roll.loc[roll.pid == pid].iloc[0, 0]
      except IndexError:
         print(f"PID {pid} not found in {args.csv}\n")
         raise

      # Convert integer section to a string 00x section, update the dataframe
      section = f'00{roll.loc[roll.pid==pid].section.iloc[0]}'
      roll.loc[roll.pid == pid, 'section'] = section
      roll.loc[roll.pid == pid, 'imageURL'] = \
         f'{dotenv_values["HTTPS_FQDN"]}/static/images/students/{onyen}.png'

      # Write out the file to static/images/students
      fn = f"../static/images/students/{onyen}.png"
      if pix.n < 5:       # this is GRAY or RGB
         pix.pil_save(fn)
      else:               # CMYK: convert to RGB first
         pix1 = fitz.Pixmap(fitz.csRGB, pix)
         pix1.pil_save("p%s-%s.png" % (i, xref))
         pix1 = None
      pix = None
      number_of_images += 1

assert number_of_images == number_of_pids, f'Read Connect Carolina PDF: The number of pids is {number_of_pids} but the number of images is {number_of_images}'

# I don't want to actually put the CSV into the database
# Let's get it into a file and let the admin verify it's correct
# They might want to merge it into the existing file, or whatever
roll.columns = ['Student ID', 'PID', 'Name', 'Section', 'imageURL']
roll.to_csv('x.csv', index=False, columns=["Student ID", "PID", "Name", "Section", "imageURL"])
print(f'./ReadClassRollIntoSQL.py csv=x.csv')
