#!/usr/bin/env python
import sys
import os.path
import datetime
import time
import json
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from data_utils import *
other_features = {}
def weather_and_operating_features_extraction_one_user(user_id):
	out_path_prefix = "/home/dehajjik/workspace/logs/"
	data = DataExtractor.load_json_data(user_id)
	known_features = (["activityRecognitionResult", "androidActivityRecognitionResult", "appLaunch", "battery", "bluetooth", "event", "notifications", "headsetPlug", "location", "networkInfo", "sensor", "settingInfo",
						"settingInfo", "telephony", "telephony2", "wifiAps", "wifiConnectedAp", "launcherLayouts", "predictors", "neighboringCellInfo2", "neighboringCellInfo" ])
	
	#filter notification already adds to the records the attributes createDateTimeZone and rcreateDateTimeZone
	#check that the data is really ordered by date!!
	data = DataOperations.filter_notifications(data)
	
	#the data is sorted and notification is filtered and annotated with the timezone date.
	for record_id in data:
		record = data[record_id]
		for key, value in record.iteritems():
			if key not in known_features:
				if key not in other_features.keys():
					other_features[key]=[]
				if len(other_features[key])<100:
					other_features[key].append(value)
	
	
	t = time.strftime("%Y%m%d")
	t = t+""+time.strftime("%H%M%S")
	JsonUtils.save_json_data(out_path_prefix+"/"+t+"extra_features_u"+str(user_id), other_features)
	return other_features