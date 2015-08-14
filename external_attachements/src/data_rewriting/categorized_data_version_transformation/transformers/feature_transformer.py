#!/usr/bin/env python
import sys
from abc import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from clean_data_utils import *

'''
feature transformer is an "observer" that is responsible for the transformation of one specific feature.
It is an abstract class
'''
class FeatureTransformer:
	__metaclass__ = ABCMeta
	#timeout is set to the equivalent of 60 minutes. if the same activity occurs in delta time smaller or equal to timeout, then we assume that, this activity was occuring in between
	timeout_in_millis = 1000*60*60
	def __init__(self, nontransformed_data):
		#the initial version of the cleaned and not transformed data
		self.nontransformed_data = nontransformed_data
		
		#the data after transformation
		self.transformed_feature_data = {}
		
		#the metadata information about the data
		self.transformed_feature_metadata= {}
	
		self.negation_value_constant = -1
	
	@abstractmethod
	def transform(self):
		return None
		
	
	'''
	this method takes a piece of data and concatenate the realization if:
		1-they are the same
		2-occured in a time interval less than timeout_in_millis
		
	must take an ordered data (chronologically ordered)
	
	return an ordered chronologically data
	'''
	def concatenate_successive_realizations(self, ordered_data):
		concatenated_data = {}
		current_realization = None
		current_date = None
		
		for date, realization in ordered_data.iteritems():
			if current_realization == None:
				#it is the first iteration
				current_realization = realization
				current_date = date
				
			else:
				deltatime_millis = DataExtractor.end_date_of_realization_in_millis(date)-DataExtractor.start_date_of_realization_in_millis(current_date)
				if current_realization != realization or deltatime_millis > self.timeout_in_millis:
					#add the current realization to the data and start building a new one
					concatenated_data[current_date]=current_realization
					current_date = date
					current_realization = realization
				
				elif current_realization == realization and deltatime_millis <= self.timeout_in_millis:
					#concatenate the two dates
					current_date = DataOperations.union_of_date_intervals_soft_version(current_date , date)
				else:
					raise Exception("UNEXPECTED BRANCK EXCEPTION: program in an unexpected branch")
					
		concatenated_data[current_date]=current_realization
		concatenated_data = collections.OrderedDict(sorted(concatenated_data.items()))
		
		return concatenated_data