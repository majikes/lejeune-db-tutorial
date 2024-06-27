#! /usr/bin/python3
"""Process the tmd files and turn them into Reveal-md md files"""

# Currently this code assumes the .env file has FQDN, HTTPS_FQDN, HOSTNAME, PIAZZA, and LOGO

from glob import glob
import os
from datetime import datetime
import re
import dotenv
from jinja2 import Template

# Get the variables from the .env file
dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

def process_tmd_files():
   """ Process each TMD file, runing it through Markdown and Jinja processing
       put output in corresponding .md file
   """

   # Process each file ending in tmd
   updated_a_tmd = False
   tmd_filenames = glob('*.tmd')
   for tmd_filename in tmd_filenames:
      # compare the date of the corresponding tmd and md files
      md_filename = re.sub(r'.tmd$', r'.md', tmd_filename)
      tmd_mtime = datetime.fromtimestamp(os.path.getmtime(tmd_filename))
      try:
         md_mtime = datetime.fromtimestamp(os.path.getmtime(md_filename))
      except FileNotFoundError:
         md_mtime = datetime.fromtimestamp(0)

      # If the md file is older, process it
      if md_mtime < tmd_mtime:
         print(f'updateReveal: updating {tmd_filename} into {md_filename}')
         with open(tmd_filename) as fid:
            try:
               template = Template(fid.read())
            except Exception as e:
               print(f'\nFailed to do Jinja translation for {tmd_filename}. '
                     f'Probably sytax error within double curly brackets\n')
               raise

         dotenv_values['TITLE'] = re.sub(r'.tmd$', r'', tmd_filename)
         md_data = template.render(dotenv_values)  # Replace FRAG an other environment variables

         with open(md_filename, 'w') as fid:
            fid.write(md_data)
         updated_a_tmd = True

   if not updated_a_tmd:
      print('updateReveal: no tmd files to update')

if __name__ == "__main__":
   process_tmd_files()
