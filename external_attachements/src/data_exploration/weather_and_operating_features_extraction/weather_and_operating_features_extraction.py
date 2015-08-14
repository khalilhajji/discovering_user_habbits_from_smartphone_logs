#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import json
import collections
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from data_utils import *
other_features = {}
def weather_and_operating_features_extraction_one_user(user_id):
	out_path_prefix = "/home/dehajjik/workspace/logs/"
	data = DataExtractor.load_json_data(user_id)
	known_features = (["activityRecognitionResult", "androidActivityRecognitionResult", "appLaunch", "battery", "bluetooth", "event", "notifications", "headsetPlug", "location", "networkInfo", "sensor", "settingInfo",
						"settingInfo", "telephony", "telephony2", "wifiAps", "wifiConnectedAp", "launcherLayouts", "predictors" ])
	
	#filter notification already adds to the records the attributes createDateTimeZone and rcreateDateTimeZone
	#check that the data is really ordered by date!!
	data = DataOperations.filter_notifications(data)
	
	#the data is sorted and notification is filtered and annotated with the timezone date.
	for record_id in data:
		record = data[record_id]
		for key, value in record.iteritems():
			key not in known_features:
				if key not in other_features:
					other_features[key]=[]
				other_features[key].append(record)
				print key+"\n"
	
	
	t = time.strftime("%Y%m%d")
	t = t+""+time.strftime("%H%M%S")
	JsonUtils.save_json_data(out_path_prefix+str(DataExtractor.user_long_ids[user_id])+"/"+t+"extra_features_u"+str(user_id), other_features)
	return other_features