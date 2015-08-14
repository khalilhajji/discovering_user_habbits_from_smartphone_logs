'''
This file contains utils operations that are done on the matrix version of the data.
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
from datetime import *
import numpy as np
import collections
from json_utils import JsonUtils
import pickle

'''
MRVFDataExtractor is the class that handles all the data extraction operations of the categorized version of the data
'''
class RVFDataExtractor:
	test_user_id = 7
	user_long_ids = {1: 358240050409564,
	2:351680061098293,
	3:357662053603904,
	4:352136065024396,
	5:359801050338118,
	6:357662053135337,
	7:352136065015162}
	
	rvf_data_dir =  "/speech/dbwork/mul/students/dehajjik/rfv_data/"
	
	
	rvf_data_path = "/all/rfv_file"
	rvf_featuresnames_path = "/all/features_names"
	rvf_valuesnames_path = "/all/values_names"
	rvf_recordsnames_path ="/all/records"
	
	#the 7th user is just for testing. Only called by the test methods
	user_data_path={1:rvf_data_dir+str(user_long_ids[1]),
	2: rvf_data_dir+str(user_long_ids[2]),
	3: rvf_data_dir+str(user_long_ids[3]),
	4: rvf_data_dir+str(user_long_ids[4]),
	5: rvf_data_dir+str(user_long_ids[5]),
	6: rvf_data_dir+str(user_long_ids[6]),
	7: rvf_data_dir+str(352136065015162)}
	
	'''
	returns the rvf data for the specified user
	the rows dimention represent the features and the columns the time
	'''
	@staticmethod
	def load_rvf(user_id):
		print "loading the matrix from "+RVFDataExtractor.user_data_path[user_id]
		with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_data_path) as f:
			data = pickle.load(f)
			
		with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_featuresnames_path, 'rb') as f:
			featuresnames = pickle.load(f)
		
		with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_valuesnames_path, 'rb') as f:
			valuesnames = pickle.load(f)
		
		with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_recordsnames_path, 'rb') as f:
			recordsdates = pickle.load(f)
		
		return [data, featuresnames, valuesnames, recordsdates]
	

	'''
	writes the matrix data for the specified user
	'''
	@staticmethod
	def save_rvf(user_id, data, featuresnames, valuesnames, recordsdates):
			print "saving the matrix in "+RVFDataExtractor.user_data_path[user_id]
			with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_data_path, 'wb') as f:
				pickle.dump(data, f)
			
			with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_featuresnames_path, 'wb') as f:
				pickle.dump(featuresnames, f)
			
			with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_valuesnames_path, 'wb') as f:
				pickle.dump(valuesnames, f)
			
			with open(RVFDataExtractor.user_data_path[user_id]+RVFDataExtractor.rvf_recordsnames_path, 'wb') as f:
				pickle.dump(recordsdates, f)
		
	'''
	return the all the users' id's as a list of integer
	'''
	@staticmethod
	def users_ids_list():
		users = RVFDataExtractor.user_long_ids.keys()[0:6]
		users.remove(3)
		return users
		
			
		
	
	
	

