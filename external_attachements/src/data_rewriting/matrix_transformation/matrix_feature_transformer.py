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
from dateutil import rrule
from datetime import datetime, timedelta
import numpy.ma as ma




'''
It transforms a categorized feature to a matrix format:
	- a 2 dimentional numpy array where the firt dimention (rows) represents the time and the second dimantion (columns) represents a cococcuring vector
	- an array containing the labels of the dimentions
'''
class MatrixFeatureTransformer (object):
	
	
	
	hour_precision = "hour"
	minute_precision = "minute"
	quarter_hour_precision = "quarter_hour"
	
	'''
	data: categorized data -> {feature_name: feature_data},
	metadata: metadata containing the meaning of the data -> {feature_name: feature_data}, 
	start_data: datetime object containig thedate of the first record that we have about the user (all features included), 
	end_date: datetime object containig thedate of the first record that we have about the user (all features included), 
	coocurring_precision: string that can takes one of the precisions value indicated as class attributes indicating the precison taken into account to consider two events as co_occuring
	'''
	def __init__(self, feature, data, metadata, start_date, end_date, coocurring_precision):
		self.metadata = metadata
		self.feature_name = feature
		#sort the data by increasing date
		self.data = data
		self.data = collections.OrderedDict(sorted(self.data.items()))
		
		self.time_vector = self.create_dates_vector(start_date, end_date, coocurring_precision)
		self.labels_vector = self.create_labels_vector(self.metadata)
		#a 2 dimentional numpy array where the firt dimention (rows) represents the time and the second dimantion (columns) represents a cococcuring vector
		self.matrix_data = np.zeros((len(self.time_vector), len(self.labels_vector)))
		self.nbdimentions = len(self.labels_vector)
		
		
		self.coocurring_precision=coocurring_precision
		
		self.realization_importance_score = np.ones(len(self.labels_vector))
		
		self.let_importance_scores_to_1 = False
		
		self.feature_coef = 1
		self.do_normalize = True
		
		
	

		
	'''
	does the transformation of the data into the matrix format. constructs and fills matrix_data
	'''
	def transform(self):
		data_copy = copy.deepcopy(self.data)
		if self.coocurring_precision==MatrixFeatureTransformer.hour_precision:
			time_id = 0
			for target_date in self.time_vector:
				#mark all the realizations that correspond to target_date
				for date_interval in data_copy.keys():
					realization = data_copy[date_interval]
					#get all the hours representing the interval
					start_realization_time = DateTimeUtils.round_to_the_hour_before(DataExtractor.start_date_of_realization(date_interval))
					end_realization_time = DateTimeUtils.round_to_the_hour_before(DataExtractor.end_date_of_realization(date_interval))
					
					
					
					hours = DateTimeUtils.hours_between(start_realization_time , end_realization_time)
					do_break = False
					
					for hour in hours:
						
						if hour == target_date:
							#integrate the vector to the column time_id of the matrix
							vector = self.transform_realization_to_vector(realization)
							self.matrix_data[time_id, : ] = self.vector_transformer_operator(self.matrix_data[time_id, : ],vector)
						
						if hour>target_date:
							#we need to advance the target date
							do_break = True
							break
						
					if do_break:
						break
					
					del data_copy[date_interval]
				time_id +=1
			
			if not self.let_importance_scores_to_1:
				self.realization_importance_score = self.ir_importance_score(self.matrix_data)
			print "the number of non zeros for "+self.feature_name+" values is : "+str(np.count_nonzero(self.matrix_data))+"/"+str(np.size(self.matrix_data))
			
		elif self.coocurring_precision == MatrixFeatureTransformer.quarter_hour_precision:
			time_id = 0
			for target_date in self.time_vector:
				#mark all the realizations that correspond to target_date
				for date_interval in data_copy.keys():
					realization = data_copy[date_interval]
					#get all the hours representing the interval
					start_realization_time = DateTimeUtils.round_to_the_quarter_before(DataExtractor.start_date_of_realization(date_interval))
					end_realization_time = DateTimeUtils.round_to_the_quarter_before(DataExtractor.end_date_of_realization(date_interval))
					quarters = DateTimeUtils.quarterhours_between(start_realization_time , end_realization_time)
					do_break = False
					
					#print "date interval is "+date_interval
					#print "hours are "+str(quarters)
					#print "target date is "+str(target_date)
					
					#print 
					#print 
					
					for quarter in quarters:
						
						if quarter == target_date:
							#integrate the vector to the column time_id of the matrix
							vector = self.transform_realization_to_vector(realization)
							self.matrix_data[time_id, : ] = self.vector_transformer_operator(self.matrix_data[time_id, : ],vector)
						
						if quarter>target_date:
							#we need to advance the target date
							do_break = True
							break
						
						#if quarter<target_date:
							#raise Exception("UNEXPECTED BRANCH EXCEPTION ")
							
					if do_break:
						break
					
					del data_copy[date_interval]
				time_id +=1
			
			if not self.let_importance_scores_to_1:
				self.realization_importance_score = self.ir_importance_score(self.matrix_data)
			
			
			
			'''
			for testing 
			'''
			'''self.matrix_data = np.zeros((4,8))
			self.matrix_data[0,0]=1
			self.matrix_data[2,0]=1
			self.matrix_data[0,1]=1
			self.matrix_data[3,2]=1
			#----
			self.matrix_data[1,5]=1
			self.matrix_data[3,5]=1
			self.matrix_data[1,6]=1
			self.matrix_data[2,6]=1
			self.matrix_data[2,7]=1'''
			
			
			[self.matrix_data, self.time_vector] = self._do_aggregated_special_transformation_with_replative_importance(self.matrix_data, 4, self.feature_coef, self.time_vector,self.do_normalize)
			print np.shape(self.matrix_data)
			print len(self.time_vector)
			print "the number of non zeros for "+self.feature_name+" values is : "+str(np.count_nonzero(self.matrix_data))+"/"+str(np.size(self.matrix_data))
			
			
			
			
		
		else:
			raise Exception("NOT IMPLEMENTED EXCEPTION : Branch coocurring_precision "+coocurring_precision+" not yet implemented ")
		
	
	'''
	create the dates vector, the vector containing all the different dates that are evaluated in the matrix. The ith date corresponds to the ith column of the matrix
	'''
	def create_dates_vector(self,start_date, end_date, coocurring_precision):
		if coocurring_precision==MatrixFeatureTransformer.hour_precision:
			start_date = DateTimeUtils.round_to_the_hour_before(start_date)
			end_date = DateTimeUtils.round_to_the_hour_after(end_date)
			time_vector = DateTimeUtils.hours_between(start_date , end_date)
			
		
		elif coocurring_precision == MatrixFeatureTransformer.quarter_hour_precision:
			start_date = DateTimeUtils.round_to_the_hour_before(start_date)
			end_date = DateTimeUtils.round_to_the_hour_after(end_date)
			time_vector = DateTimeUtils.quarterhours_between(start_date , end_date)[0:-1]
			#print time_vector
		
		
			
			
			
		
		else:
			raise Exception("NOT IMPLEMENTED EXCEPTION : Branch coocurring_precision "+coocurring_precision+" not yet implemented ")
			
		print "start_date "+str(start_date)
		print "end_date "+str(end_date)
		print coocurring_precision
		print "number of date values "+str(len(time_vector))
			
		return time_vector
	
	'''
	This transformation does the following:
		-sums the columns k by k where k is the aggregation_nb
		- after aggregation normalizes each column so that it sums to 1 (or 0 if it is empty)
		- multiply all the matrix by a factor equal to multipling_factor
	'''
	def _do_aggregated_special_transformation_with_replative_importance(self, matrix, aggregation_nb, multipling_factor, times_vector, do_normalize):
		#note: we just transpose the matrix to match the code and then we transpose the result again at the end of the method
		t_matrix = np.transpose(matrix)
		columns_nb = np.size(t_matrix, 1)
		rows_nb = np.size(t_matrix,0)
		if columns_nb%aggregation_nb == 0:
			#aggregation number is okay
			ag_column_size = columns_nb/aggregation_nb
			ag_matrix = np.zeros((rows_nb, columns_nb/aggregation_nb))
			ag_times_vector = []
			k = aggregation_nb
			#do the aggregation, normalize and multiply by the factor
			for i in range(0,ag_column_size):
				vector = np.sum(t_matrix[:,i*k:(i+1)*k],1)
				ag_times_vector.append(times_vector[i*k])
				sum = np.sum(vector,0)
				if sum != 0:
					if do_normalize: ag_matrix[:,i] = (vector/sum)*multipling_factor;
					else: ag_matrix[:,i] = (vector)*multipling_factor;
				
				else:
					ag_matrix[:,i] = vector
			ag_matrix = np.transpose(ag_matrix)	
			return [ag_matrix,ag_times_vector]
			
			
		
		else:
			raise Exception("BAD INPUT EXCEPTION: the aggregation number ("+str(aggregation_nb)+") and the number of columns ("+str(columns_nb)+") do not match.")
	
	'''
	create the labels vector, the vector containing the labels that corrsponds to the different dimention of the record vectors. The ith row corresponds to the ith label
	'''	
	def create_labels_vector(self, metadata):
		labels = []
		id_labels_dict = {}
		
		#we should only have one feature, so this iteration is only of order of 1
		feature_name = self.feature_name
			
			
		for attribute, attribute_info in metadata.iteritems():
			attribute_name = attribute
				
			for realization_id, id_info in attribute_info.iteritems():
		
				complete_label = feature_name+"__"+attribute_name+"__"+self.get_attribute_label(realization_id, id_info)
				id_labels_dict[int(realization_id)] = complete_label
				
			
		id_labels_dict= collections.OrderedDict(sorted(id_labels_dict.items()))
		labels = id_labels_dict.values()
	
					
		return labels	
	
	
	'''
	inverse rank importance score : attributes an importance score to each realization r computed as following (#possible_realizations-rank_r)/(#possible_realizations)
	where rank is 0 for the most frequent realizations and #possible_realizations-1 for the less frequent
	returns a numpy vector containing the importance of each realization
	'''
	def ir_importance_score(self, matrix):
		#first compute the number of times each realization occurs
		realizations_count = (matrix==1).sum(0)
		
		#get the rank of each realization from the counts
		ranked_indicies = realizations_count.argsort()
		realizations_rank = np.empty(len(ranked_indicies), int)
		realizations_rank[ranked_indicies]=np.arange(len(ranked_indicies))
		
		#compute the score for each realization
		nb_realizations = np.size(matrix,1)
		
		ir_importance_scores = ((nb_realizations-realizations_rank)*1.0)/nb_realizations
		
		return ir_importance_scores
		
	'''
	frequency importance score : attributes an importance score to each realization r computed as following (#occurences_r)/(#occurences_most_frequent_realization)
	returns a numpy vector containing the importance of each realization
	'''
	def f_importance_score(self, matrix):
		#first compute the number of times each realization occurs
		realizations_count = (matrix==1).sum(0)
		
		#get the number of occurences of the realization that occured the most
		max_count = realizations_count.max()
		
		#compute the score for each realization
		f_importance_scores = realizations_count/(max_count*1.0)
		
		return f_importance_scores
		
	'''
	from the realization and the id_info returns the label of this realization
	'''
	def get_attribute_label(self, realization_id, id_info):
		return id_info
	
	'''
	defines the operation between two vectors. takes two vectors as input and returns one vector as output
	'''
	def vector_transformer_operator (self, vector1, vector2):
		vfunc = np.vectorize(self.elemenwise_transformer_operator)
		v_result =  vfunc(vector1, vector2)
		
		return v_result
	
	'''
	the possible values that an element of a vector can contain are:
		1: this attribute is present
		-1: this attribute is absent
		0: we don't know if this attribute is present or absent
		
	Thus the elementwise function is:
		(0,0)->0
		(0,1)->1
		(0,-1)->-1
		(1,-1)->1
		(1,1)->1
		(-1,-1)->-1	
	'''	
	def elemenwise_transformer_operator(self, a, b):
		#the operations done in the next lines is equivalent to the one described in the comments
		value = self.sign((a+b)/2)* math.ceil(abs((a+b)/2))
		if value == 0 and (a == 1 or a == -1):
			value = 1
		if value == 0 and (a!=0 or b!= 0):
			raise Exception("a : "+str(a)+" b : "+str(b)+" val : "+str(value))
			
		
		if value not in [-1,0,1]:
			raise Exception("UNEXCPECTED VALUE EXCEPTION: vector contains value "+str(a)+" and the other "+str(b)+"--> they give :"+str(value))
			
		return value
	
	def sign(self, a):
		if a>= 0:
			return 1
		else :
			return -1

	'''
	takes a categorized realization an outputs an nparray vector representing the vector representation of this realization
	'''
	def transform_realization_to_vector(self, realization):
		#create a vector with the required number of elements
		vector = np.zeros((self.nbdimentions))
		#we get the list of all possible attributes
		attributes = self.metadata.keys()
		for attribute in attributes :
			#for each attribute we get the list of its ids and then we check if it is present in the current realization
			id_range = sorted(self.metadata[attribute].keys(), key= lambda k: int(k))
			min_id = int(id_range[0])
			max_id = int(id_range[-1])
			
			if attribute in realization:
				#we set all the realizations to not present
				#vector[min_id:(max_id+1)] = -1
				vector[min_id:(max_id+1)] = 0
				
				
				
				#then we set the realization(s) that is present to present
				id_realization = realization[attribute]
				if id_realization != -1:		
					vector[id_realization]=1
				
		
					
			#else:
				#this attribute is unknown for this realization, so we let it a zero
				
		 	
		return vector

	
	
	
	
	
'''
	The location matrix transformer. Has the way to retreive the attributes label that is different	
'''
class MatrixLocationFeatureTransformer (MatrixFeatureTransformer):
	def __init__(self,feature, data, metadata, start_date, end_date, coocurring_precision):
		MatrixFeatureTransformer.__init__(self,feature, data, metadata, start_date, end_date, coocurring_precision)
			
	'''
	from the realization and the id_info returns the label of this realization
	'''
	def get_attribute_label(self, realization_id, id_info):
		return str(realization_id)
		

'''
The bleutooth matrix transformer. Has the way to retreive the attributes label that is different
'''		
class MatrixBleutoothFeatureTransformer (MatrixFeatureTransformer):
	transformed_feature_metabluetooth_name =  "name"
	def __init__(self,feature, data, metadata, start_date, end_date, coocurring_precision):
		MatrixFeatureTransformer.__init__(self,feature, data, metadata, start_date, end_date, coocurring_precision)
			
	'''
	from the realization and the id_info returns the label of this realization
	'''
	def get_attribute_label(self, realization_id, id_info):

		device_names = id_info[self.transformed_feature_metabluetooth_name]
		label = ""
		for name in device_names:
			label += "_"+name
		
		label = label [1:]
		return label
		
		
class MatrixTimeFeatureTransformer():
	number_of_days = 7
	number_of_hours = 23
	feature_name="time"
	day_label="day"
	hour_label = "hour"
	
	
	
	#means that the first range is between 0h-6h, the second between 6h-12h, the third between 12-18h and the last 18h-0h
	hours_division_4 = [0,6,12,18]
	hours_division_3 = [0,9,16]
	
	def __init__(self, start_date, end_date, coocurring_precision):
		self.time_vector = self.create_dates_vector(start_date, end_date, coocurring_precision)
		self.labels_vector = self.create_labels_vector(self.hours_division_3)
		#a 2 dimentional numpy array where the firt dimention (rows) represents the time and the second dimantion (columns) represents a cococcuring vector
		self.matrix_data = np.zeros((len(self.time_vector), len(self.labels_vector)))
		self.nbdimentions = len(self.labels_vector)
		self.nbtimeslots = len(self.time_vector)
		
		self.let_importance_scores_to_1 = False
		self.feature_coef = 1
		self.coocurring_precision = coocurring_precision
		
		
		
	

		
	'''
	does the transformation of the data into the matrix format. constructs and fills matrix_data
	'''
	def transform(self):
		time_id = 0
		for target_date in self.time_vector:
			self.matrix_data[time_id, : ] = self.transform_date_to_vector(target_date, self.hours_division_3)
			time_id +=1
			
		if self.coocurring_precision == MatrixFeatureTransformer.quarter_hour_precision:	
			[self.matrix_data, self.time_vector] = self._do_aggregated_special_transformation_with_replative_importance(self.matrix_data, 4, self.feature_coef, self.time_vector)
			self.nbdimentions = len(self.labels_vector)
			self.nbtimeslots = len(self.time_vector)
			
		
		self.days_matrix = self.matrix_data[:,0:self.number_of_days]
		self.hours_matrix = self.matrix_data[:, self.number_of_days: ]
		
		if not self.let_importance_scores_to_1:
			#the importance scores need to be computed separately for the date and the time, because they represent two independent features
			days_importance_score = self.f_importance_score(self.days_matrix)
			hours_importance_score = self.f_importance_score(self.hours_matrix)
			self.realization_importance_score = np.concatenate((days_importance_score, hours_importance_score))
		
		print np.shape(self.matrix_data)
		print len(self.time_vector)
		print "the number of non zeros for "+self.feature_name+" values is : "+str(np.count_nonzero(self.matrix_data))+"/"+str(np.size(self.matrix_data))
	
	'''
	create the dates vector, the vector containing all the different dates that are evaluated in the matrix. The ith date corresponds to the ith column of the matrix
	'''
	def create_dates_vector(self, start_date, end_date, coocurring_precision):
		if coocurring_precision==MatrixFeatureTransformer.hour_precision:
			start_date = DateTimeUtils.round_to_the_hour_before(start_date)
			end_date = DateTimeUtils.round_to_the_hour_after(end_date)
			time_vector = DateTimeUtils.hours_between(start_date , end_date)
			return time_vector
		
		elif coocurring_precision == MatrixFeatureTransformer.quarter_hour_precision:
			start_date = DateTimeUtils.round_to_the_hour_before(start_date)
			end_date = DateTimeUtils.round_to_the_hour_after(end_date)
			time_vector = DateTimeUtils.quarterhours_between(start_date , end_date)[0:-1]
		
			return time_vector
		
		else:
			raise Exception("NOT IMPLEMENTED EXCEPTION : Branch coocurring_precision "+coocurring_precision+" not yet implemented ")
			
		
	
	
	'''
	inverse rank importance score : attributes an importance score to each realization r computed as following (#possible_realizations-rank_r)/(#possible_realizations)
	where rank is 0 for the most frequent realizations and #possible_realizations-1 for the less frequent
	returns a numpy vector containing the importance of each realization
	'''
	def ir_importance_score(self, matrix):
		#first compute the number of times each realization occurs
		realizations_count = (matrix==1).sum(0)
		
		#get the rank of each realization from the counts
		ranked_indicies = realizations_count.argsort()
		realizations_rank = np.empty(len(ranked_indicies), int)
		realizations_rank[ranked_indicies]=np.arange(len(ranked_indicies))
		
		#compute the score for each realization
		nb_realizations = np.size(matrix,1)
		
		ir_importance_scores = ((nb_realizations-realizations_rank)*1.0)/nb_realizations
		
		return ir_importance_scores
		
	'''
	frequency importance score : attributes an importance score to each realization r computed as following (#occurences_r)/(#occurences_most_frequent_realization)
	returns a numpy vector containing the importance of each realization
	'''
	def f_importance_score(self, matrix):
		#first compute the number of times each realization occurs
		realizations_count = (matrix==1).sum(0)
		
		#get the number of occurences of the realization that occured the most
		max_count = realizations_count.max()
		
		#compute the score for each realization
		f_importance_scores = realizations_count/(max_count*1.0)
		
		return f_importance_scores
		
		
	'''
	create the labels vector, the vector containing the labels that corrsponds to the different dimention of the record vectors. The ith row corresponds to the ith label
	'''	
	def create_labels_vector(self, hours_division):
		labels = []
		#add the labels corresponding to the day
		day_name = None
		for day_id in range(0, self.number_of_days):
			if 0 == day_id: day_name="monday"; 
			elif 1 == day_id: day_name="tuesday"; 
			elif 2 == day_id: day_name="wednesday"; 
			elif 3 == day_id: day_name="thursday";
			elif 4 == day_id: day_name="friday";
			elif 5 == day_id: day_name="saturday";
			elif 6 == day_id: day_name="sunday";
			label = self.feature_name+"_"+self.day_label+"_"+day_name
			labels.append(label)
		
		if hours_division == None:
			#add the labels corresponding to the hour
			for hour_id in range(0, self.number_of_hours):
				label = self.feature_name+"_"+self.hour_label+"_"+str(hour_id)
				labels.append(label)
				
		else:
			
			next_i = 1
			for hour_start in hours_division:
				if next_i >= len(hours_division):
					next_i = 0
				hour_end = hours_division[next_i]
				label = self.feature_name+"_"+self.hour_label+"_"+str(hour_start)+"_"+str(hour_end)
				labels.append(label)
				next_i+=1
					
		return labels	
		
	'''
	This transformation does the following:
		-sums the columns k by k where k is the aggregation_nb
		- after aggregation normalizes each column so that it sums to 1 (or 0 if it is empty)
		- multiply all the matrix by a factor equal to multipling_factor
	'''
	def _do_aggregated_special_transformation_with_replative_importance(self, matrix, aggregation_nb, multipling_factor, times_vector):
		#note: we just transpose the matrix to match the code and then we transpose the result again at the end of the method
		print np.shape(self.matrix_data)
		print len(self.time_vector)
		t_matrix = np.transpose(matrix)
		columns_nb = np.size(t_matrix, 1)
		rows_nb = np.size(t_matrix,0)
		if columns_nb%aggregation_nb == 0:
			#aggregation number is okay
			ag_column_size = columns_nb/aggregation_nb
			ag_matrix = np.zeros((rows_nb, ag_column_size))
			ag_times_vector = []
			k = aggregation_nb
			#do the aggregation, normalize and multiply by the factor
			for i in range(0,ag_column_size):
				vector = t_matrix[:,i*k]
				ag_times_vector.append(times_vector[i*k])
				ag_matrix[:,i] = vector*multipling_factor
				
				
			ag_matrix = np.transpose(ag_matrix)	
			return [ag_matrix,ag_times_vector]
			
			
		
		else:
			raise Exception("BAD INPUT EXCEPTION: the aggregation number ("+str(aggregation_nb)+") and the number of columns ("+str(columns_nb)+") do not match.")
		
	'''
	transforms a date to a vector
	'''
	def transform_date_to_vector(self, date, hours_division):
		hour = date.hour
		if hours_division == None:
			hours_vector = [0]*self.number_of_hours
			hours_vector[hour] = 1
		else: 
			hours_vector = [0]*len(hours_division)
			next_i = 1
			current_i = 0 
			for hour_start in hours_division:
				if next_i >= len(hours_division):
					hours_vector[current_i] = 1
					break;
				
				hour_end = hours_division[next_i]
				if hour >= hour_start and hour < hour_end:
					hours_vector[current_i] = 1
					break;
				current_i += 1 
				next_i+=1
			
		
		day = date.weekday()
		days_vector = [0]*self.number_of_days
		days_vector[day] = 1
		
		return days_vector+hours_vector
		
	
				
		