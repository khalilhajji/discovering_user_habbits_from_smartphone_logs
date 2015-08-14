#!/usr/bin/env python
import sys
import collections
import pprint as pp
import copy
from datetime import *
sys.path.insert(0, "/home/dehajjik/workspace/src/data_rewriting/matrix_transformation")
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from categorized_data_utils import *
from json_utils import JsonUtils
from date_time_utils import DateTimeUtils
import math
import numpy as np
from dateutil import rrule
from datetime import datetime, timedelta
import numpy.ma as ma
from matrix_feature_transformer import *




'''
It transforms a categorized feature to a a set of array of values:
	- each array contains the values taken by one record ex:[0,0,1,2] which means that record takes 2 times the value 0 and one time the value 1 and one time the value 2
'''
class ValuesFeatureTransformer (object):

	'''
	data: categorized data -> {feature_name: feature_data},
	metadata: metadata containing the meaning of the data -> {feature_name: feature_data}, 
	start_data: datetime object containig thedate of the first record that we have about the user (all features included), 
	end_date: datetime object containig thedate of the first record that we have about the user (all features included), 
	coocurring_precision: string that can takes one of the precisions value indicated as class attributes indicating the precison taken into account to consider two events as co_occuring
	'''
	def __init__(self, object, feature, data, metadata, start_date, end_date, coocurring_precision):
		if  issubclass(object,MatrixFeatureTransformer):
			print "is object a Matrix Feature Transfomer : "+str(object)+" --> "+str(issubclass(object,MatrixFeatureTransformer))
			self.matrix_transformer = object(feature, data, metadata, start_date, end_date, coocurring_precision)
			
		else:
			raise Exception("NON CONFORM TYPE EXCEPTIOM: the object passed in parameters is not a feature matrix transformer class : "+str(object))
		
		self.matrix_transformer.do_normalize = False  #We just want the counts and not the probabilities
		self.feature_name = feature
		self.matrix_data = None
		self.values_data = None
		self.values_labels = None
		self.records_dates= None
		
	'''
	does the transformation of the data into the values format 
	'''
	def transform(self):
		self.matrix_transformer.transform()    #First step transform the data as a matrix
		self.matrix = np.transpose(self.matrix_transformer.matrix_data)
		self.records_dates = self.matrix_transformer.time_vector
		self._init_values_labels()
		self._remove_non_occuring_values()
		self._transform_to_values_data()
		
		
	def _init_values_labels(self):
		prefix_len = len(self.feature_name+"__")
		self.values_labels = [value_name[prefix_len:] for value_name in self.matrix_transformer.labels_vector]
		print "instantiation of values labels : "+str(self.values_labels)
		
	def _transform_to_values_data(self):
		self.values_data = []
		records_nb = np.size(self.matrix,1)
		
		for r in range(records_nb):
			positions = np.nonzero(self.matrix[:,r])[0]
			values = []   								   #for each record r instantiate an empy list of values
			for pos in positions:						   #fill the list values for record r
				values += ([pos]*int(self.matrix[pos,r]))  #position repeated number of occurrences time
				
			self.values_data.append(values)				   #append the values of record r to the values_data
			
		print self.matrix[:,0:10]
		print self.values_data[0:10]
		
	def _remove_non_occuring_values(self):
		values_to_keep = np.logical_not(np.all(self.matrix == 0, axis=1))
		new_labels = [self.values_labels[i] for i in range(len(self.values_labels)) if values_to_keep[i] ]
		print "values to keep"
		print values_to_keep
		
		print new_labels
		self.matrix = self.matrix[values_to_keep,:]
		self.values_labels = new_labels
			
class ValuesTimeFeatureTransformer (object):
	day_label="day"
	hour_label = "hour"
	'''
	data: categorized data -> {feature_name: feature_data},
	metadata: metadata containing the meaning of the data -> {feature_name: feature_data}, 
	start_data: datetime object containig thedate of the first record that we have about the user (all features included), 
	end_date: datetime object containig thedate of the first record that we have about the user (all features included), 
	coocurring_precision: string that can takes one of the precisions value indicated as class attributes indicating the precison taken into account to consider two events as co_occuring
	'''
	def __init__(self, object, feature, start_date, end_date, coocurring_precision):
		
		if  issubclass(object,MatrixTimeFeatureTransformer):
			print "is object a Matrix Feature Transfomer : "+str(object)+" --> "+str(issubclass(object,MatrixTimeFeatureTransformer))
			self.matrix_transformer = object(start_date, end_date, coocurring_precision)
			
		else:
			raise Exception("NON CONFORM TYPE EXCEPTIOM: the object passed in parameters is not a time feature matrix transformer class.")
		
		self.matrix_transformer.do_normalize = False  #We just want the counts and not the probabilities
		self.feature_name = feature
		self.time_matrix_data = None
		self.day_matrix_data = None
		self.time_values_data = None
		self.day_values_data = None
		self.time_values_labels = None
		self.day_values_labels = None
		self.records_dates= None
		
	'''
	does the transformation of the data into the values format 
	'''
	def transform(self):
		self.matrix_transformer.transform()    #First step transform the data as a matrix
		self.time_matrix_data = np.transpose(self.matrix_transformer.hours_matrix)
		self.day_matrix_data = np.transpose(self.matrix_transformer.days_matrix)
		print "day matrix"
		print self.day_matrix_data
		
		print "time matrix"
		print self.time_matrix_data
		
		self.records_dates = self.matrix_transformer.time_vector
		self._init_values_labels()
		self._transform_to_values_data()
		
		
		
		
	def _init_values_labels(self):
		day_prefix = self.feature_name+"_"+ValuesTimeFeatureTransformer.day_label+"_"
		time_prefix = self.feature_name+"_"+ValuesTimeFeatureTransformer.hour_label+"_"
		print self.matrix_transformer.labels_vector
		self.day_values_labels = [value_name[len(day_prefix):] for value_name in self.matrix_transformer.labels_vector if day_prefix in value_name]
		self.time_values_labels = [value_name[len(time_prefix):] for value_name in self.matrix_transformer.labels_vector if time_prefix in value_name]
				
		print "instantiation of values labels : "
		print self.day_values_labels
		print self.time_values_labels
		
	def _transform_to_values_data(self):
		self.day_values_data = []
		self.time_values_data = []
		records_nb = np.size(self.time_matrix_data,1)
		
		for r in range(records_nb):
			t_positions = np.nonzero(self.time_matrix_data[:,r])[0]
			time_values = []   								   #for each record r instantiate an empy list of values
			for pos in t_positions:						   #fill the list values for record r
				time_values += ([pos]*int(self.time_matrix_data[pos,r]))  #position repeated number of occurrences time
			self.time_values_data.append(time_values)				   #append the values of record r to the values_data
			
			d_positions = np.nonzero(self.day_matrix_data[:,r])[0]
			day_values = []   								   #for each record r instantiate an empy list of values
			for pos in d_positions:						   #fill the list values for record r
				day_values += ([pos]*int(self.day_matrix_data[pos,r]))  #position repeated number of occurrences time
			self.day_values_data.append(day_values)
