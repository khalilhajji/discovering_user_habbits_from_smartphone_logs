#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from compute_lcbmf_one_user import compute_lcbmf_one_user as clou

from matrix_data_utils import *
'''
make the categorized data transformation for all the users
'''
for user_id in MDataExtractor.users_ids_list():
	print("user "+str(user_id)+" on working")
	clou(user_id)
	
	print("user "+str(user_id)+" extracted")