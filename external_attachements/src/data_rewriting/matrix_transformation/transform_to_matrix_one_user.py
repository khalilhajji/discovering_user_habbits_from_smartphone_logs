#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from categorized_data_utils import DataExtractor
from datetime import *
import numpy as np
import collections
from matrix_feature_transformer import *
from numpy_utils import Numpy
from matrix_data_utils import *

'''
transform the categorized data of a user to a matrix where:
	- the first dimention (rows) represents the features
	- the second dimention (columns) represents the time
	
	+ thus a columns represents a vector that represents co-occuring events:
		- 1 means that the event is present
		- -1 means that the event is absent
		- 0 means that we do not know if it was present or absent
'''
#change the repository of output in MDataExtractor in function of the coocuring precision chosen
coocurring_precision = "hour"
#coocurring_precision = "quarter_hour"
date_min = datetime(1970, 1, 1, 00, 00, 00)
features_importance_score_one = ["headset", "battery"]
def transform_to_matrix_one_user(user_id):
	
		
	print "loading data for user "+str(user_id)
	categorized_data = DataExtractor.load_json_data(user_id)
	data = DataExtractor.complete_data(categorized_data)
	metadata = DataExtractor.complete_metadata(categorized_data)
	
	#order the data by the alphabetic name of the features
	print "ordering data "+str(user_id)
	data = collections.OrderedDict(sorted(data.items()))
	
	#get the first date and the last date
	print "getting first date and last date "
	end_date = date_min
	start_date = datetime.now()
	for feature, feature_data in data.iteritems():
		feature_data = collections.OrderedDict(sorted(feature_data.items()))
		begin_date = DataExtractor.start_date_of_realization(feature_data.keys()[0])
		if begin_date < start_date:
			start_date = begin_date
			
		last_date = DataExtractor.start_date_of_realization(feature_data.keys()[len(feature_data.keys())-1])
		if last_date > end_date:
			end_date = last_date
		
		data[feature] = feature_data
	
	#construct the data matrix
	#I- construct the matrices of all the features
	print "constructing the matrixes "
	rows = 0
	
	transformers = {} 
	for feature, feature_date in data.iteritems():
		if feature == "location":
			transformers[feature] = MatrixLocationFeatureTransformer(feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
		elif feature == "bluetoothSeen" or feature == "bluetoothPaired":
			transformers[feature] = MatrixBleutoothFeatureTransformer(feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
		else :
			transformers[feature] = MatrixFeatureTransformer(feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
			
		if feature in features_importance_score_one:
			transformers[feature].let_importance_scores_to_1 = True
		
		transformers[feature].transform()
		rows += transformers[feature].nbdimentions
	
	#construct the time feature
	transformers[MatrixTimeFeatureTransformer.feature_name] = MatrixTimeFeatureTransformer(start_date, end_date, coocurring_precision)
	transformers[MatrixTimeFeatureTransformer.feature_name].transform()
	rows +=  transformers[MatrixTimeFeatureTransformer.feature_name].nbdimentions
	columns = transformers[MatrixTimeFeatureTransformer.feature_name].nbtimeslots
	
	#II-concatenate all the matrices of each feature into one big matrix (do the same for the labels vector)
	print "regrouping the matrixes "
	data_matrix = np.zeros((columns, rows))
	labels_vector = [""]* rows
	dimentions_importance_score = np.zeros(rows)
	transformers = collections.OrderedDict(sorted(transformers.items()))
	
	begin_row_idex = 0
	end_row_index = 0
	for feature, feature_transformer in transformers.iteritems():
		end_row_index = begin_row_idex + feature_transformer.nbdimentions
		data_matrix[:, begin_row_idex:end_row_index] =  feature_transformer.matrix_data
		labels_vector[begin_row_idex:end_row_index] = feature_transformer.labels_vector
		dimentions_importance_score[begin_row_idex:end_row_index]=feature_transformer.realization_importance_score
		begin_row_idex = end_row_index
	
	'''
	The matrix contains a lot of feature vectors that contains 0 in all the features except the time features.
	Those vectors corresponds to the times where any record has been done.
	We want to eliminate those timestamps and their corresponding times
	'''
	time_vector = transformers.values()[0].time_vector
	[data_matrix, time_vector] = eliminate_empty_records(data_matrix, time_vector)
	data_matrix = np.transpose(data_matrix)
	
	print "the labels are : "
	print JsonUtils.dict_as_json_str(labels_vector)
	
	
	print "first date of observation "+str(start_date)
	print "first date of observation "+str(end_date)
	print "dimension of the labels (features) vector : "+str(len(labels_vector))
	print "dimension of the time vector : "+str(len(time_vector))
	print "dimension of the resulted matrix (features, time) "+str(data_matrix.shape)
	print "the number of non zeros values is : "+str(np.count_nonzero(data_matrix))+"/"+str(np.size(data_matrix))
	print "the number of negative values in the matrix is : "+str(np.size(ma.masked_array(data_matrix, mask=(data_matrix>=0)).compressed()))
	print "the data matrix printed : "
	print Numpy.str(data_matrix)
	
	#write the matrix data
	MDataExtractor.save_matrix(user_id, data_matrix)
	
	#write the labels vector, then the time vector and the importance scores
	MDataExtractor.save_labels_vector(user_id, labels_vector)
	MDataExtractor.save_time_vector(user_id, time_vector)
	MDataExtractor.save_importance_scores(user_id, dimentions_importance_score)
	
'''
The matrix contains a lot of feature vectors that contains 0 in all the features except the time features.
Those vectors corresponds to the times where any record has been done.
We want to eliminate those timestamps and their corresponding times

returns a new matrix with the empty records eliminated and the new corresponding time vector
'''	
def eliminate_empty_records(matrix, time_vector):
	#the vectors that contain only the time stamp will have exactly 2 ones.
	
	#first we count the number of ones in each vector
	#ones_count_vector = (matrix==1).sum(1)
	ones_count_vector = (matrix>0).sum(1)
	
	#second we construct a vector that contains 1 if the number of ones is bigger than 2 (thus needs to be keeped), 0 otherwise (note that sum function applied to a boolean array will just sum the number of true entries)
	mask_vector = (ones_count_vector>2)
	
	#eliminate the rows that corresponding to the indicies of 0 and keep the indicies of 1 in the matrix
	matrix_new = matrix[mask_vector,:]
	
	#eliminate the empty records dates from the time vector
	unmasked_inidicies = np.arange(len(mask_vector))[mask_vector]
	
	time_vector_new = [time_vector[i] for i in unmasked_inidicies]
	
	
	return [matrix_new, time_vector_new]
	
	
	
	