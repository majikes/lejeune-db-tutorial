#!/usr/bin/env python3
""" Read a Connect Carolina PDF of student pictures with the corresponding
    Sakai CSV to create a classroll.csv file of students, pids, names and pictures
    that would be read by ReadClassRollIntoSQL.py
"""

# Need to pip3 install pymupdf

import Args
import base64
import fitz
import dotenv
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

args = Args.Parse(pdf=str,
                  verbose=0,
                 )

# doc = fitz.open("Chapter.01.pdf")
doc = fitz.open(args.pdf)
number_pages = len(doc)
tmd_output_fn = 'x.tmd'
tmd_output_str = """---
title: {{TITLE}}
theme: "comp421"
separator: "^---"
verticalSeparator: "^----"
notesSeparator: "^Note:"
revealOptions:
    transition: fade

"""


def remove_attrs(soup, whitelist=tuple()):
    ''' Remove all attributes because markdown doesn't most of them '''
    for tag in soup.findAll(True):
        for attr in [attr for attr in tag.attrs if attr not in whitelist]:
            del tag[attr]
    return soup

def remove_span(soup):
    ''' Remove all span's because markdown doesn't support it '''
    for match in soup.findAll('span'):
        match.unwrap()
    return soup

def cleanup_html(soup):
    soup = remove_attrs(soup, whitelist=('src'))
    soup = remove_span(soup)
    return soup

output_fn = 'A'
def convert_images(soup):
    global output_fn
    for i in soup.findAll('img'):
        del i['style']
        b64data = i['src'][len('data:image/jpeg;base64/n'):]
        try:
           img = Image.open(BytesIO(base64.b64decode(str(b64data))))
           img.save(f'{output_fn}.jpg', 'JPEG')
        except Exception as e:
            print(f'Ignoring an image due to exception: {e}')
        i['src'] = f'{output_fn}.jpg'
        temp = ord(output_fn)
        temp += 1
        output_fn = chr(temp)
    return soup

# Read all the PIDS from the Text part of the PDF
# Note that a PID must be 9 characters long and an integer
# Ignore all other text
for page_number in range(number_pages):
   page_html = doc.get_page_text(page_number, 'html')
   soup = BeautifulSoup(page_html, 'html.parser')
   soup = convert_images(soup)
   soup = cleanup_html(soup)

   ## Remove the outermost div around the page and append this to the current slide deck
   soup.find('div').unwrap()
   tmd_output_str += f"""
---
{soup}"""


with open(tmd_output_fn, "w", encoding="UTF-8") as f:
    f.write(tmd_output_str)

print(f'{tmd_output_fn} has the reveal formatted output')
