#!/usr/bin/env python
import sys
import collections
import pprint as pp
import copy
from datetime import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from categorized_data_utils import *
from json_utils import JsonUtils
from date_time_utils import DateTimeUtils
import math
import numpy as np
from datetime import datetime, timedelta
import numpy.linalg as linalg
import collections



'''

'''
class SVDComputer (object):
	
	
	#this repesents the % of the absolute value of the whole matrix that should be captured to accept the approximation
	energy = 80
	
	k_label = "k"
	
	'''
	
	'''
	def __init__(self, matrix, row_labels, columns_labels):
		#the data_matrix
		self.x_matrix = matrix
		self.row_labels = row_labels
		self.columns_labels = columns_labels
		self.energy = None
		
		#those represents the resulting matrixes from the decompositon X_hat = U.D.V with ||X-X_hat|| small
		self.u_matrix = None
		self.s_vector = None
		self.v_matrix = None
		
		self.rows_interpretable_output = {}
		
		print "the number of non zeros values is : "+str(np.count_nonzero(self.x_matrix))+"/"+str(np.size(self.x_matrix))
	

		
	'''
	computes a matrix svd decomposition 
	'''
	def compute_svd(self):
		[self.u_matrix, self.s_vector, self.v_matrix] = linalg.svd(self.x_matrix, full_matrices=False, compute_uv=True)
		

	
	'''
	compute the % of energy captured by the k biggest dimentions
	More specifically, the square of each
	singular value is proportional to the variance explained by each singular vector -> which is equivalent to the percentage of ||X-X_hat||^2 comparing to ||X||^2
	'''	
	def energy_captured_percentage(self, k):
		#the sum of the singular values
		s_squared = self.s_vector * self.s_vector 
		s_squared_sum = linalg.norm(s_squared, ord= 1)*1.0
		s_normalized = s_squared/s_squared_sum
		energy_captured_percentage = np.sum(s_normalized[0:k])*100
		
		return energy_captured_percentage
		
	
	'''
	from the realization and the id_info returns the label of this realization
	nb_concepts: nb of concepts to display, 
	nb_features_display: for each concept the number of features to display
	NB: the square of each singular value is proportional to the variance explained by each singular vector
	'''
	def construct_rows_interpretable_output(self, nb_concepts, nb_features_display):
		#the sum of the singular values
		s_squared = self.s_vector * self.s_vector 
		s_squared_sum = linalg.norm(s_squared, ord= 1)*1.0
		s_normalized = s_squared/s_squared_sum
		
		#vector containing the sum of each column
		u_norms = (linalg.norm(self.u_matrix, ord= 1, axis = 0)*1.0)
		#divide each column by its sum
		u_normalized = self.u_matrix/u_norms
		
		#built the interpretable output as a dictionary
		self.rows_interpretable_output[self.k_label] = {}
		for k in range(0, nb_concepts):
			kth_key = str(k)+" : "+str(s_normalized[k])
			self.rows_interpretable_output[self.k_label][kth_key]={}
			kth_output={}
			kth_vector = u_normalized[:,k]
			
			nb_rows = None
			if np.size(kth_vector) == len(self.row_labels):
				nb_rows = np.size(kth_vector)
			else:
				raise Exception("NON MATCHING LENGTHS EXCEPTIONS: the columns vector has size "+size(kth_vector)+" whereas the corresponding number of labels is "+len(self.row_labels))
				
			for m in range(0, nb_rows):
				kth_output[self.row_labels[m]] = kth_vector[m]
				
			
			kth_output = collections.OrderedDict(sorted(kth_output.items(), key=lambda item: abs(item[1]), reverse= True)[0:nb_features_display]) 
			self.rows_interpretable_output[self.k_label][kth_key] = kth_output
			
			self.rows_interpretable_output[self.k_label] = collections.OrderedDict(sorted(self.rows_interpretable_output[self.k_label].items(), key=lambda item: int(item[0].split(" : ")[0]))) 
			
		print "computing energy ..."
		return self.energy_captured_percentage(k)
			
			
		
		
	
				
		