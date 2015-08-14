#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from compute_ghcm_mdt_one_user import compute_ghcm_mdt_one_user as cgou

from rfv_data_utils import RVFDataExtractor

'''
make the categorized data transformation for all the users
'''
for user_id in RVFDataExtractor.users_ids_list():
	print("user "+str(user_id)+" on working")
	cgou(user_id)
	
	print("user "+str(user_id)+" extracted")
