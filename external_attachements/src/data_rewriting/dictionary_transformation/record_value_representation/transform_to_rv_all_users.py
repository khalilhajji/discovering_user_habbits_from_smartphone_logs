#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from transform_to_rv_one_user import transform_to_rv_one_user as ttrou
from rv_data_utils import RVDataExtractor


'''
make the categorized data transformation for all the users
'''
for user_id in RVDataExtractor.users_ids_list():
	ttrou(user_id)
	
	print("user "+str(user_id)+" extracted")
	print 
