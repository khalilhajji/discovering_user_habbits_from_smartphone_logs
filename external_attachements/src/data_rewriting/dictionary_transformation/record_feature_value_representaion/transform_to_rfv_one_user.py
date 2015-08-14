#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from categorized_data_utils import DataExtractor
from datetime import *
import numpy as np
import collections
from value_feature_transformer import *
from numpy_utils import Numpy
from matrix_data_utils import *
from rfv_data_utils import RVFDataExtractor

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
coocurring_precision = "quarter_hour"
date_min = datetime(1970, 1, 1, 00, 00, 00)
nonpersistent_features = ["bluetoothPaired", "notification", "appLaunch"] #the features that are punctual and not always happening (location is persistent, appLaunch not persistent)
nonpresent_v = "not_present"
def transform_to_rfv_one_user(user_id):
	
		
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
	
	#construct the values data
	#I- construct the values for all the features
	print "constructing the values data"
	
	transformers = {} 
	features_name = []
	records = []
	values_name = {}
	for feature, feature_date in data.iteritems():
		if feature == "location":
			transformers[feature] = ValuesFeatureTransformer(MatrixLocationFeatureTransformer, feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
		elif feature == "bluetoothSeen" or feature == "bluetoothPaired":
			transformers[feature] = ValuesFeatureTransformer(MatrixBleutoothFeatureTransformer, feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
		else :
			transformers[feature] = ValuesFeatureTransformer(MatrixFeatureTransformer, feature, data[feature], metadata[feature], start_date, end_date, coocurring_precision)
			
		transformers[feature].transform()
		features_name.append(feature)
		values_name[features_name.index(feature)] = transformers[feature].values_labels
		
	
	
	#construct the time feature
	feature = "time"
	timetrans = ValuesTimeFeatureTransformer(MatrixTimeFeatureTransformer, feature, start_date, end_date, coocurring_precision)
	timetrans.transform()
	transformers[ValuesTimeFeatureTransformer.day_label] =  timetrans
	transformers[ValuesTimeFeatureTransformer.hour_label] =  timetrans
	features_name.append(ValuesTimeFeatureTransformer.day_label)
	values_name[features_name.index(ValuesTimeFeatureTransformer.day_label)] = timetrans.day_values_labels
	features_name.append(ValuesTimeFeatureTransformer.hour_label)
	values_name[features_name.index(ValuesTimeFeatureTransformer.hour_label)] = timetrans.time_values_labels
	
	records_labels =  timetrans.records_dates
	records_nb = len(records_labels)
	
	#make space for records
	for r in range(records_nb):
		records.append({})
	
	#II-fill the records
	for fid, fname in enumerate(features_name):
		if fname == ValuesTimeFeatureTransformer.day_label:
			for r in range(records_nb):
				if transformers[fname].day_values_data[r]!= []: records[r][fid] = transformers[fname].day_values_data[r];
		elif fname == ValuesTimeFeatureTransformer.hour_label:
			for r in range(records_nb):
				if transformers[fname].time_values_data[r]!= []: records[r][fid] = transformers[fname].time_values_data[r];
		else:
			for r in range(records_nb):
				if transformers[fname].values_data[r]!= []: records[r][fid] = transformers[fname].values_data[r];
	
	#remove the ones that only contain value for the time feature 
	for r in range(records_nb-1, -1, -1): #Decreasing loop over the records so that remove is possible
		if len(records[r]) <= 2:
			del records[r]
	
	#for the remaining records, add non_present values for the non_persistant features that are not present in each record. non_persistant
	for nf in nonpersistent_features: #add the non_present value as a value that can be taken by the non persistent features
		if nf in features_name: 
			nfid = features_name.index(nf)
			values_name[nfid].append(nonpresent_v)
	
	rtv_data = {}
	for idr, r in enumerate(records):
		for nf in nonpersistent_features:
			if nf in features_name:
				nfid = features_name.index(nf)
				if nfid not in r: r[nfid]=[values_name[nfid].index(nonpresent_v)];
		rtv_data[idr]=r
				
	print "first date of observation "+str(start_date)
	print "first date of observation "+str(end_date)
	print "features names "+str(features_name)
	print "values names : "+str(values_name)
	print "number of records "+str(len(rtv_data))
  
	#write the data, the record dates, the feature names and the value names
	RVFDataExtractor.save_rvf(user_id, rtv_data, features_name, values_name, records_labels)
	

	
	