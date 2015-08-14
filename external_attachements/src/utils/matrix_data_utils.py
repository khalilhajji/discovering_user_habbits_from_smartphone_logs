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
MDataExtractor is the class that handles all the data extraction operations of the categorized version of the data
'''
class MDataExtractor:
	test_user_id = 7
	user_long_ids = {1: 358240050409564,
	2:351680061098293,
	3:357662053603904,
	4:352136065024396,
	5:359801050338118,
	6:357662053135337,
	7:352136065015162}
	
	matrix_data_dir =  "/speech/dbwork/mul/students/dehajjik/matrix_data_normalized/"
	#matrix_data_dir = "/speech/dbwork/mul/students/dehajjik/matrix_data/"
	
	
	matrix_user_data_suffix = "/all/matrix_file.npy"
	matrix_user_labels_suffix = "/all/dimentions_definition_files"
	matrix_file_importance_scores = "/all/dimentions_importance_score_file.npy"
	matrix_user_time_suffix ="/all/time_vector_file"
	
	#the 7th user is just for testing. Only called by the test methods
	user_data_path={1:matrix_data_dir+str(user_long_ids[1])+matrix_user_data_suffix,
	2: matrix_data_dir+str(user_long_ids[2])+matrix_user_data_suffix,
	3: matrix_data_dir+str(user_long_ids[3])+matrix_user_data_suffix,
	4: matrix_data_dir+str(user_long_ids[4])+matrix_user_data_suffix,
	5: matrix_data_dir+str(user_long_ids[5])+matrix_user_data_suffix,
	6: matrix_data_dir+str(user_long_ids[6])+matrix_user_data_suffix,
	7: matrix_data_dir+str(352136065015162)+matrix_user_data_suffix}
	
	
	
	user_dimentionslabels_path={1:matrix_data_dir+str(user_long_ids[1])+matrix_user_labels_suffix,
	2: matrix_data_dir+str(user_long_ids[2])+matrix_user_labels_suffix,
	3: matrix_data_dir+str(user_long_ids[3])+matrix_user_labels_suffix,
	4: matrix_data_dir+str(user_long_ids[4])+matrix_user_labels_suffix,
	5: matrix_data_dir+str(user_long_ids[5])+matrix_user_labels_suffix,
	6: matrix_data_dir+str(user_long_ids[6])+matrix_user_labels_suffix,
	7: matrix_data_dir+str(352136065015162)+matrix_user_labels_suffix}
	
	user_timevector_path={1:matrix_data_dir+str(user_long_ids[1])+matrix_user_time_suffix,
	2: matrix_data_dir+str(user_long_ids[2])+matrix_user_time_suffix,
	3: matrix_data_dir+str(user_long_ids[3])+matrix_user_time_suffix,
	4: matrix_data_dir+str(user_long_ids[4])+matrix_user_time_suffix,
	5: matrix_data_dir+str(user_long_ids[5])+matrix_user_time_suffix,
	6: matrix_data_dir+str(user_long_ids[6])+matrix_user_time_suffix,
	7: matrix_data_dir+str(352136065015162)+matrix_user_time_suffix}
	
	user_importancescore_path = {1:matrix_data_dir+str(user_long_ids[1])+matrix_file_importance_scores,
	2: matrix_data_dir+str(user_long_ids[2])+matrix_file_importance_scores,
	3: matrix_data_dir+str(user_long_ids[3])+matrix_file_importance_scores,
	4: matrix_data_dir+str(user_long_ids[4])+matrix_file_importance_scores,
	5: matrix_data_dir+str(user_long_ids[5])+matrix_file_importance_scores,
	6: matrix_data_dir+str(user_long_ids[6])+matrix_file_importance_scores,
	7: matrix_data_dir+str(352136065015162)+matrix_file_importance_scores}
	
	
	
	'''
	returns the matrix data for the specified user
	the rows dimention represent the features and the columns the time
	'''
	@staticmethod
	def load_matrix(user_id):
		print "loading the matrix from "+MDataExtractor.user_data_path[user_id]
		data = np.load(MDataExtractor.user_data_path[user_id])
		return data
	

	'''
	writes the matrix data for the specified user
	'''
	@staticmethod
	def save_matrix(user_id, matrix):
			print "saving the matrix in "+MDataExtractor.user_data_path[user_id]
			np.save(MDataExtractor.user_data_path[user_id], matrix)
		
	
	'''
	returns the importance scores for the specified user
	'''
	@staticmethod
	def load_importance_scores(user_id):
		scores = np.load(MDataExtractor.user_importancescore_path[user_id])
		return scores
	

	'''
	writes the importance scores for the specified user
	'''
	@staticmethod
	def save_importance_scores(user_id, importance_scores):
		np.save(MDataExtractor.user_importancescore_path[user_id], importance_scores)
	
	
	'''
	returns a list containing the labels (meaning) of each dimention (the rows dimention)
	'''
	@staticmethod	
	def load_labels_vector(user_id):
		with open(MDataExtractor.user_dimentionslabels_path[user_id], 'rb') as f:
			labels = pickle.load(f)
			return labels
			
	
			
	'''
	writes a list containing the labels (meaning) of each dimention (the rows dimention)
	'''
	@staticmethod	
	def save_labels_vector(user_id, labels):
		with open(MDataExtractor.user_dimentionslabels_path[user_id], 'wb') as f:
			pickle.dump(labels, f)
			
	'''
	returns a list containing the different dates corresponding to each column in the matrix
	'''
	@staticmethod	
	def load_time_vector(user_id):
		with open(MDataExtractor.user_timevector_path[user_id], 'rb') as f:
			time_vector = pickle.load(f)
			return time_vector
			
	'''
	writes a list containing the labels (meaning) of each dimention (the rows dimention)
	'''
	@staticmethod	
	def save_time_vector(user_id, time_vector):
		with open(MDataExtractor.user_timevector_path[user_id], 'wb') as f:
			pickle.dump(time_vector, f)
		
		
	'''
	return the all the users' id's as a list of integer
	'''
	@staticmethod
	def users_ids_list():
		users = MDataExtractor.user_long_ids.keys()[0:6]
		users.remove(3)
		return users
		
			
		
	
	
	

