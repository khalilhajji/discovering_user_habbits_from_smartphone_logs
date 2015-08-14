#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from compute_svd_one_user import compute_svd_one_user as csou

from matrix_data_utils import *
'''
make the categorized data transformation for all the users
'''
for user_id in MDataExtractor.users_ids_list():
	print("user "+str(user_id)+" on working")
	csou(user_id)
	
	print("user "+str(user_id)+" extracted")
