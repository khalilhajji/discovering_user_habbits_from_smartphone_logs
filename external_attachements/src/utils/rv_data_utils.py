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
class RVDataExtractor:
	test_user_id = 7
	user_long_ids = {1: 358240050409564,
	2:351680061098293,
	3:357662053603904,
	4:352136065024396,
	5:359801050338118,
	6:357662053135337,
	7:352136065015162}
	
	rf_data_dir =  "/speech/dbwork/mul/students/dehajjik/rv_data/"
	
	
	rvf_data_path = "/all/rv_file"
	rvf_realizationnames_path = "/all/realizations_names"
	rvf_recordsnames_path ="/all/records"
	
	#the 7th user is just for testing. Only called by the test methods
	user_data_path={1:rf_data_dir+str(user_long_ids[1]),
	2: rf_data_dir+str(user_long_ids[2]),
	3: rf_data_dir+str(user_long_ids[3]),
	4: rf_data_dir+str(user_long_ids[4]),
	5: rf_data_dir+str(user_long_ids[5]),
	6: rf_data_dir+str(user_long_ids[6]),
	7: rf_data_dir+str(352136065015162)}
	
	'''
	returns the rvf data for the specified user
	the rows dimention represent the features and the columns the time
	'''
	@staticmethod
	def load_rv(user_id):
		print "loading the dictionary from "+RVDataExtractor.user_data_path[user_id]
		with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_data_path) as f:
			data = pickle.load(f)
			
		with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_realizationnames_path, 'rb') as f:
			realizationsnames = pickle.load(f)
		
		with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_recordsnames_path, 'rb') as f:
			recordsdates = pickle.load(f)
		
		return [data, realizationsnames, recordsdates]
	

	'''
	writes the matrix data for the specified user
	'''
	@staticmethod
	def save_rv(user_id, data, realizationsnames, recordsdates):
			print "saving the matrix in "+RVDataExtractor.user_data_path[user_id]
			with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_data_path, 'wb') as f:
				pickle.dump(data, f)
			
			with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_realizationnames_path, 'wb') as f:
				pickle.dump(realizationsnames, f)
			
			with open(RVDataExtractor.user_data_path[user_id]+RVDataExtractor.rvf_recordsnames_path, 'wb') as f:
				pickle.dump(recordsdates, f)
		
	'''
	return the all the users' id's as a list of integer
	'''
	@staticmethod
	def users_ids_list():
		users = RVDataExtractor.user_long_ids.keys()[0:6]
		users.remove(3)
		return users
		
			
		
	
	
	

