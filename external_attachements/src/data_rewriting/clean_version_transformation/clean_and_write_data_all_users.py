'''
takes the original data, cleans it and write it to the outpath in a suitable format for all the users.
To have more details about the transformation, look to clean_data_documentation file (present in the doc directory)
'''
#!/usr/bin/env python
import sys


sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from clean_and_write_data_one_user import clean_and_write_data_one_user as cawdou



for user_id in DataExtractor.users_ids_list():
	cawdou(user_id)
	print("user "+str(user_id)+" extracted")
	