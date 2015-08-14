#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from transform_to_matrix_one_user import transform_to_matrix_one_user as ttmou

from clean_data_utils import DataExtractor

'''
make the categorized data transformation for all the users
'''
for user_id in DataExtractor.users_ids_list():
	ttmou(user_id)
	
	print("user "+str(user_id)+" extracted")
	print 
