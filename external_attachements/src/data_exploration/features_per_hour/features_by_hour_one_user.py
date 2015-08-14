#!/usr/bin/env python
import sys
import os.path
import datetime
from pprint import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from plot_lib_utils import PlotlibDrawer
def features_by_hour_one_user(user_id):
	
	'''focus_periods = {1: [[datetime.datetime(year=2014, month=8, day=15, hour=0),datetime.datetime(year=2014, month=9, day=17, hour=23)],
					  [datetime.datetime(year=2014, month=10, day=1, hour=0),datetime.datetime(year=2014, month=10, day=30, hour=23)]],
				2: [[datetime.datetime(year=2014, month=9, day=1, hour=0),datetime.datetime(year=2014, month=9, day=30, hour=23)],
					  [datetime.datetime(year=2014, month=12, day=1, hour=0),datetime.datetime(year=2014, month=12, day=30, hour=23)]],
				3: [[datetime.datetime(year=2014, month=9, day=1, hour=0),datetime.datetime(year=2014, month=10, day=1, hour=23)]],
				4: [[datetime.datetime(year=2014, month=8, day=28, hour=0),datetime.datetime(year=2014, month=10, day=5, hour=23)],
					  [datetime.datetime(year=2015, month=1, day=1, hour=0),datetime.datetime(year=2015, month=1, day=15, hour=23)]],
				5: [[datetime.datetime(year=2014, month=9, day=1, hour=0),datetime.datetime(year=2014, month=9, day=30, hour=23)],
					  [datetime.datetime(year=2014, month=12, day=10, hour=0),datetime.datetime(year=2015, month=1, day=10, hour=23)]],
				6: [[datetime.datetime(year=2014, month=10, day=17, hour=0),datetime.datetime(year=2014, month=11, day=17, hour=23)]],
				7: [[datetime.datetime(year=2014, month=8, day=27, hour=0),datetime.datetime(year=2014, month=8, day=28, hour=23)]]
				}'''
	
	focus_periods = {1: [[datetime.datetime(year=2014, month=10, day=5, hour=0),datetime.datetime(year=2014, month=10, day=16, hour=23)]],
				2: [],
				3: [],
				4: [[datetime.datetime(year=2014, month=12, day=1, hour=0),datetime.datetime(year=2014, month=12, day=21, hour=23)]],
				5: [[datetime.datetime(year=2014, month=11, day=17, hour=0),datetime.datetime(year=2014, month=12, day=17, hour=23)]],
				6: [],
				7: []
				}
				
	target_features = ['notifications',
		'sensor',
		'activityRecognitionResult_activity',
		#'androidActivityRecognitionResult_activity',
		'appLaunch',
		#'battery_health',
		#'bluetooth',
		#'headsetPlug',
		'location'
		#'networkInfo_state',
		#'telephony',
		#'wifiAps',
		#'wifiConnectedAp',
	]



	data = DataExtractor.load_json_data(user_id)
	
	for periods in focus_periods[user_id]:
		#get a dictionary representing the number of features per hour in the selected period
		features_per_hour = DataOperations.features_per_hour(periods[0], periods[1], data , target_features)
		
		
		#make the plot
		#construct the plot
		y_values_matrix = []
		for dict in features_per_hour.values():
			y_values_matrix.append(dict.values())
		
		#One label each 12 hours	
		nb_labels = len(features_per_hour[target_features[0]].keys())/(12)
		PlotlibDrawer.plot(features_per_hour[target_features[0]].keys(), y_values_matrix, features_per_hour.keys(), "hours", "number records", "records per hour for user "+str(user_id)+"("+str(DataExtractor.user_long_ids[user_id])+")", nb_labels)
		