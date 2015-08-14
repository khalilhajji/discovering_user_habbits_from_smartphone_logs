"""
for each feature, test how much this feature is present in each record for one user (the json data file of that user
is given as argument). For each feature, outputs a percentage  between 0 and 100. 100% means that the feature is present in 100% 
of the records, 0% means that is present in 0% of the records. 
"""
#!/usr/bin/env python
import sys
import json
import os
from pprint import *

def features_presence_rate_one_user(file_name):
	json_data=open(file_name).read()
	data = json.loads(json_data)
	
	features_counter_array = {'activityRecognitionResult_activity' : 0,
	'activityRecognitionResult_motion': 0,
	'activityRecognitionResult_carrying' : 0,
	'activityRecognitionResult_posture' : 0,
	'androidActivityRecognitionResult_activity' : 0,
	'appLaunch' : 0,
	'battery_health' : 0,
	'bluetooth' : 0,
	'notifications' : 0,
	'headsetPlug' : 0,
	'location' : 0,
	'networkInfo_state' : 0,
	'telephony' : 0,
	'wifiAps' : 0,
	'wifiConnectedAp' : 0
	}
	
	
	records_counter = 0.0
	
	for record in data['logInfo']:
		records_counter+=1
		for key, value in data['logInfo'][record].iteritems():
			if key == 'activityRecognitionResult':
				if value['activity'] != 'Unrecognizable motion':
					features_counter_array['activityRecognitionResult_activity'] +=1
				if value['motion'] != 'Unnkown' :
					features_counter_array['activityRecognitionResult_motion']+=1
				if value['carrying'] != 'unknown':
					features_counter_array['activityRecognitionResult_carrying']+=1
				if value['posture'] != 'unknown':
					features_counter_array['activityRecognitionResult_posture']+=1
			elif key == 'androidActivityRecognitionResult' and value['activity'] != 'unknown':
				features_counter_array['androidActivityRecognitionResult_activity'] +=1
			elif key == 'battery' and value['health'] != 1 and value['health'] != 'Battery health is unknown':
				features_counter_array['battery_health']+=1
			elif key == 'networkInfo' and value['state'] != 'UNKNOWN':
				features_counter_array['networkInfo_state']+=1
			elif key in features_counter_array.keys():
				features_counter_array[key]+=1
	
	for key, value in features_counter_array.iteritems():
		features_counter_array[key] = (value/records_counter)*100
	
	str = pformat (features_counter_array)
	return str
			
				
	