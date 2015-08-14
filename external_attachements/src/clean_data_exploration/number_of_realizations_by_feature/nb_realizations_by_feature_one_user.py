'''
outputs the number of realizations(events) for each feature for one user
'''
#!/usr/bin/env python
import sys
import json
import os
import datetime
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from clean_data_utils import DataExtractor

def nb_realizations_by_feature_one_user(user_id):
	
	data = DataExtractor.load_json_data(user_id)
	observation_period = [300.0, 231.0, 89.0, 249.0, 229.0,224.0]
	realizations_by_feature = {}
	realization_per_day_by_feature = {}
	
	for feature in data:
		realizations_by_feature[feature]=len(data[feature])
		realization_per_day_by_feature[feature]= len(data[feature])/observation_period[user_id-1]
	
	
	
	str_res = ('user '+str(user_id)+'('+str(DataExtractor.user_long_ids[user_id])+': \nnumber of realizations by feature:\n'+pformat(realizations_by_feature)+'\n average number of realizations per day per feature:\n'+pformat(realization_per_day_by_feature)+'\n\n')
	
	
	return str_res