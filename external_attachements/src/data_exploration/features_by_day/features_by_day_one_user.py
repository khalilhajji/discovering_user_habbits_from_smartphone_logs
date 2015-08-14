'''
plots representing the number of records by day for some features for one user.
The user_id is given as input.

The method show() of PlotlibDrawer needs to be called when all the plots ends to see the plot.

It also outputs a dictionary representing the number of records by date for the selected features for that user.
It is in the following form:
['feature_name_1']:[date1]=nb_records1
				   [date2]=nb_records2...
				   
Also note that the dictionary is sorted in the increasing order
'''
#!/usr/bin/env python
import sys
import json
import datetime
import collections
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from plot_lib_utils import PlotlibDrawer
from data_utils import *

def features_by_day_one_user(user_id):
	features_counter_per_day = {'activityRecognitionResult_activity' : {},
	'androidActivityRecognitionResult_activity' : {},
	'appLaunch' : {},
	'battery_health' : {},
	'bluetooth' : {},
	'notifications' : {},
	'headsetPlug' : {},
	'location' : {},
	'networkInfo_state' : {},
	'telephony' : {},
	'wifiAps' : {},
	'wifiConnectedAp' : {},
	'sensor' : {}
	}
	data = DataExtractor.load_json_data(user_id)
	
	first_record_date = datetime.date(2020,1,1)
	last_record_date = datetime.date(1970,1,1)
	for record_id in data:
		current_date = DataExtractor.date_of_record(data[record_id])
		current_date_str = current_date.strftime('%Y-%m-%d')
		
		for key, value in data[record_id].iteritems():
			#used to compute the first and the last record
			if current_date > last_record_date:
				last_record_date = current_date
			if current_date<first_record_date:
				first_record_date=current_date
			
			#get the feature (=key of features_counter_per_day) corresponding to this entry
			feature = DataOperations.give_me_feature(features_counter_per_day.keys(),key,value)
			
			if feature != None:
				if current_date_str not in features_counter_per_day[feature]:
					features_counter_per_day[feature][current_date_str]=0
				#the feature corresponding to this entry belongs to the features that we want to record
				#increase the counter of the corresponding feature by 1
				features_counter_per_day[feature][current_date_str]+=1
	
	
	#fill all the missing dates between the first record and the last record for all the features
	for feature,counter_by_day in features_counter_per_day.iteritems():
		features_counter_per_day[feature]= DataOperations.fill_in_between_with_zeros(counter_by_day, first_record_date, last_record_date, 'days')
		#sort the dictionary by increasing dates
		features_counter_per_day[feature] = collections.OrderedDict(sorted(counter_by_day.items()))
	
	
	#construct the plot
	y_values_matrix = []
	for dict in features_counter_per_day.values():
		y_values_matrix.append(dict.values())
		
	
	#One label per 2 weeks	
	nb_labels = len(features_counter_per_day['androidActivityRecognitionResult_activity'].keys())/15
	PlotlibDrawer.plot(features_counter_per_day['androidActivityRecognitionResult_activity'].keys(), y_values_matrix, features_counter_per_day.keys(), "days", "number records", "records per day for user "+str(user_id)+"("+str(DataExtractor.user_long_ids[user_id])+")", nb_labels)
	
	
	return features_counter_per_day