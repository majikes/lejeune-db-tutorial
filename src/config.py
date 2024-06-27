"""
Configuration inputs used to manage multiple MYPOLL deployments

See README.txt for more information
"""
import dotenv
import os
from datetime import datetime, date

# pylint: disable=eval-used

dotenv.load_dotenv()
dotenv_values = dotenv.dotenv_values()

admins = os.getenv('ADMINS')
assert admins, 'You must set ADMINS variable in .env'
admins = eval(admins)
assert isinstance(admins, list), \
   f'ADMINS={admins}, but must be a string that can be eval\'s into a Python list of strings'
assert all(isinstance(admin, str) for admin in admins), \
   f'ADMINS={admins}, but must be a string that can be eval\'s into a Python list of strings'

assessment_folders = os.getenv('ASSESSMENT_FOLDERS')
assert assessment_folders, 'You must set ASSESSMENT_FOLDERS variable in .env'
assessment_folders = eval(assessment_folders)
msg = (f'ASSESSMENT_FOLDERS={assessment_folders}, but must be a string that can be '+
       'eval\'s into a Python list of strings')
assert isinstance(assessment_folders, list), msg
assert all(isinstance(assessment_folder, str) for assessment_folder in assessment_folders), msg

assessment_dict = eval(os.getenv('ASSESSMENT_DICT'))  # Get env value and conver to Python dict
assert assessment_dict, 'You must set ASSESSMENT_DICT variable in .env'
assessment_types = list(assessment_dict.keys())

assessment_folder_dict = eval(os.getenv('ASSESSMENT_FOLDER_DICT'))  # Get env value and conver to Python dict
assert assessment_folder_dict, 'You must set ASSESSMENT_DICT variable in .env'

valid_sections = os.getenv('VALID_SECTIONS')
valid_sections = eval(valid_sections)  # Convert to python list
assert valid_sections, 'You must set VALID_SECTIONS variable in .env'
assert all([isinstance(x, str) for x in valid_sections]), 'Each element of VALID_SECTIONS must be a string'
assert all([len(x) == 3 for x in valid_sections]), 'Each element of VALID_SECTIONS must be a 3 character string'

admin_email = os.getenv('ADMIN_EMAIL')
assert admin_email, 'You must set ADMIN_EMAIL variable in .env'

gmail_user = dotenv_values['GMAIL_USER']
gmail_host = dotenv_values['GMAIL_HOST']

hostname = dotenv_values['HOSTNAME']
assert len(hostname)

postgres_pw = dotenv_values['POSTGRES_PW']
