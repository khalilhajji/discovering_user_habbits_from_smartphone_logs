#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from extract_specific_date_time_one_user import extract_specific_date_time_one_user as esdtou

for user_id in DataExtractor.users_ids_list():
	esdtou(user_id)
	print("user "+str(user_id)+" extracted")
	