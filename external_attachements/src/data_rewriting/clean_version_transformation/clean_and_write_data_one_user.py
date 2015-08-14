'''
takes the original data, cleans it and write it to the outpath in a suitable format for one given user.
To have more details about the transformation, look to clean_data_documentation file (present in the doc directory)
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import json
import collections
import copy
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from data_utils import *
blacklisted_features = ["launcherLayouts", "predictors"]
splitted_features = ["activityRecognitionResult_other","androidActivityRecognitionResult_other","battery_other"]

#if we do not have any information about one feature more than timeout minutes, we immediately create a new realization
#here we fix it to 1 hour
timeout_in_minutes = 60

#if one of these values appear in a feature realization, we just remove it
blacklisted_values = {"location": {"latitude": [0], "longitude": [0]},
					"telephony" : {"cdmaCellLocBaseStationLat":[0], "cdmaCellLocBaseStationLng":[0]},
					"telephony2": {"cdmaCellLocBaseStationLat":[0], "cdmaCellLocBaseStationLng":[0]},
					"wifiAps": {"ssid":[""]
								#,"bssId":["00:00:00:00:00:00"]
								},
					"wifiConnectedAp": {"ssid":[""]
										#,"bssId":["00:00:00:00:00:00"]
										},
					"activityRecognitionResult": {"activity" : ["unknown" , ""],
												  "motion" : ["unknown" , ""]},
					}


def clean_and_write_data_one_user(user_id):
	#empty the lists
	global clean_data
	clean_data = {}
	global last_realization_val
	last_realization_val = {}
	global last_realization_key
	last_realization_key = {}
	
	
	'''
	For each feature, we want to know what are the distribution of the difference of time observed between two realizations.
	For that reason we store in time_variances for each feature, the number of times that the difference between two realizations was x minutes.
	Note that the maximum time variance allowed is timeout_in_minutes.
	'''
	global time_variances
	time_variances ={}
	
	out_path_prefix = "/speech/dbwork/mul/students/dehajjik/clean_data/"
	data = DataExtractor.load_json_data(user_id)
	DataOperations.print_times_for_specific_locations(data)
	#filter notification already adds to the records the attributes createDateTimeZone and rcreateDateTimeZone
	#check that the data is really ordered by date!!
	data = DataOperations.filter_notifications(data)
	
	
	
	#the data is sorted and notification is filtered and annotated with the timezone date.
	for record_id in data:
		record = data[record_id]
		event_type = record['event']['type']
		for key, value in record.iteritems():
			#test if it has one black listed value, if it is the case ignore it
			do_ignore = False
			is_array_attribute = False
			if key in blacklisted_values:
				for attribute, black_values in blacklisted_values[key].iteritems():
					try :
						if value[attribute] in black_values:
							#the current realization contains one blacklisted value, so we need to ignore it
							do_ignore = True
					except TypeError:
						#the feature we have is an array feature
						is_array_attribute=True
						break;
						
			if is_array_attribute:
				#the feature we have is an array feature, so we go throught all the elements and we remove the blacklisted ones if they exist
				temp_value = []
				do_remove = False
				for one_value in value:
					for attribute, black_values in blacklisted_values[key].iteritems():
						if one_value[attribute] in black_values:
							do_remove = True
							
					if not do_remove:
						temp_value.append(one_value)
						
				if len(temp_value)>=1:
					value = temp_value
				else:
					#all the values were removed so ignore this entry
					do_ignore = True
					
			
			if not do_ignore:
				if key == "activityRecognitionResult":
					activityRecognitionResult_update(value , event_type)
				elif key == "androidActivityRecognitionResult":
					androidActivityRecognitionResult_update(value, event_type)
				elif key == "appLaunch":
					appLaunch_update(value , event_type)
				elif key == "battery":
					battery_update(value, event_type)
				elif key == "bluetooth":
					bluetooth_update(value, event_type)
				elif key == "event":
					event_update(value, event_type)
				elif key == "notifications":
					notifications_update(value, event_type)
				elif key == "headsetPlug":
					headsetPlug_update(value, event_type)
				elif key == "location":
					location_update(value, event_type)
				elif key == "networkInfo":
					networkInfo_update(value, event_type)
				elif key == "sensor":
					sensor_update(value, event_type)
				elif key == "settingInfo":
					settingInfo_update(value, event_type)
				elif key == "telephony" or key=="telephony2":
					telephony_update(value, event_type)
				elif key == "wifiAps":
					wifiApps_update(value , event_type)
				elif key == "wifiConnectedAp":
					wifiConnectedApp_update(value, event_type)
				'''elif key not in blacklisted_features:
					print key+"\n"'''
				
	
	
	
	order_data()
	#do some tests to see that the transformation went well
	do_sanity_check(data,clean_data)
	JsonUtils.save_json_data(out_path_prefix+str(DataExtractor.user_long_ids[user_id])+"/all/all_in_one_validated_log", clean_data)
		
	return clean_data
	
	

def activityRecognitionResult_update(value , event_type):
	arr_main = {'activity': value['activity'] ,
				'motion': value['motion'],
				'posture': value['posture']
				}			
	arr_main = add_common_attributes(arr_main, event_type)
	
	arr_other = {'carrying': value['carrying'] ,
				'screen': value['screen'],
				'usb': value['usb']
				}
	arr_other = add_common_attributes(arr_other, event_type)
				
	add_realization_for_interval_event("activityRecognitionResult_main" , arr_main, get_date_key(value),[] )
	add_realization_for_interval_event("activityRecognitionResult_other" , arr_other, get_date_key(value), [] )

	
	
def androidActivityRecognitionResult_update(value, event_type):
	try:
		#transform the strings representing the confidence as integers
		value['confidence'] = int(value['confidence'])
		conf_int = []
		for conf in value['confidences'].split(","):
			conf_int.append(int(conf))
		
		value['confidences'] = conf_int
		
		if "" in value['activities'].split(","):
			int("this is a caused exception in purpose")
		
		#transform the activities represented as unique string into a list of strings
		value['activities'] = value['activities'].split(",")
		
		#if no exception is raised then all the confidences are integers and thus we can add safely this entry
		aarr_main = {'activity': value['activity'],
				'confidence': [value['confidence']]
				}
					
		aarr_other = {'activities':value['activities'],
					'confidences' : value['confidences']
					}
					
		aarr_main = add_common_attributes(aarr_main, event_type)
		aarr_other = add_common_attributes(aarr_other, event_type)
		add_realization_for_interval_event("androidActivityRecognitionResult_main" , aarr_main, get_date_key(value), [] )
		add_realization_for_interval_event("androidActivityRecognitionResult_other" , aarr_other, get_date_key(value), ['confidences', 'activities'] )
			
	except ValueError:
		#useless line
		print ("")
		
			
	
	
			
def	appLaunch_update(value, event_type):
	appLaunch = add_attributes(['appName'], [], value, event_type, True)
	add_realization_for_ponctual_event("appLaunch" , appLaunch, get_date_key(value))
	
			
def battery_update(value, event_type):
	batry_main = add_attributes(['health','status', 'plugged', 'present'], [], value, event_type, True)
	batry_other = add_attributes(['level','scale', 'technology', 'temperature', 'voltage'], [], value, event_type, True)
	
	add_realization_for_interval_event("battery_main" , batry_main, get_date_key(value), [] )
	add_realization_for_interval_event("battery_other" , batry_other, get_date_key(value), [] )

			
def bluetooth_update(value, event_type):
	add_realization_for_interval_array_event("bluetooth", value, event_type, get_date_key(value), ['address','bondState','name','type'], [])
	#add_realization_for_interval_array_event("bluetooth", value, event_type, ['address','bondState','name','type'], [])
	
			
def event_update(value, event_type):
	event = add_attributes(['type', 'timeZone', 'timeZoneOffset'], [], value, event_type, True)
	add_realization_for_ponctual_event("event" , event, get_date_key(value))
			
def notifications_update(value, event_type):
	add_realization_for_ponctual_event_array_event("notification", value, event_type, get_date_key(value))
	
			
def headsetPlug_update(value, event_type):
	headset = add_attributes(['microphone', 'name', 'state'], [], value, event_type, True)
	add_realization_for_interval_event("headsetPlug" , headset, get_date_key(value), [] )

	
def location_update(value, event_type):
	if value["accuracy"]==0:
		raise Exception("0.0 accuracy whereas long and lat non 0")
	location = add_attributes(['latitude','longitude'],['accuracy', 'altitude', 'bearing', 'elapsedRealtimeNanos', 'provider', 'speed'],value,event_type,True)
	add_realization_for_interval_event("location" , location, get_date_key(value), [] )
			
def networkInfo_update(value, event_type):
	networkInfo = add_attributes(['available', 'connected', 'detailState', 'reason', 'roaming', 'state', 'type', 'typeName'], ['detailState', 'extraInfo', 'subType', 'subTypeName'], value, event_type, True)
	add_realization_for_interval_event("networkInfo" , networkInfo, get_date_key(value), [] )
			
def sensor_update(value, event_type):
	add_realization_for_ponctual_event_array_event("sensor", value, event_type, get_date_key(value))
	
def settingInfo_update(value, event_type):
	settingInfo = add_attributes('-all', [], value, event_type, True)
	add_realization_for_interval_event("settingInfo" , settingInfo, get_date_key(value), [] )
		
			
def telephony_update(value, event_type):
	telephony = add_attributes(['cdmaCellLocBaseStationId', 'cdmaCellLocBaseStationLat', 'cdmaCellLocBaseStationLng', 'networkRoming'], ['gsmCellLocCid','gsmCellLocLac', 'gsmCellLocPrc', 'networkOperator','networkOperatorName','networkType','networkTypeName', 'phoneType', 'phoneTypeName','subscriberId'], value, event_type, True)
	add_realization_for_interval_event("telephony" , telephony, get_date_key(value), [] )
	
def wifiApps_update(value, event_type):
	add_realization_for_interval_array_event("wifiAps", value, event_type, get_date_key(value), ['bssId', 'capabilities','frequency','level','ssid'], ['rcreateDateTimeZone'])
	#add_realization_for_interval_array_event("wifiAps", value, event_type, ['bssId', 'capabilities','frequency','level','ssid'], [])


			
def wifiConnectedApp_update(value, event_type):
	wca = add_attributes(['bssId', 'ssid'], ['level','linkSpeed', 'networkId', 'rssi'], value, event_type, True)
	add_realization_for_interval_event("wifiConnectedAp" , wca, get_date_key(value), [] )

'''
compares all the attributes that are not arrays, if all are the same, then the realization is concatenated with the previous one
Otherwise a new realization is created containing the new values and the attribute changed that contains the attributes that have changed.
All the attributes that are arrays are not compared but simply merged at the moment of the realization merge.
However there an exception for the latter statement:
all the attributes that are in sensitive_array_attributes are array attributes that will be treated as the normal ones. This means that 
they are sensitive to change and if the array of the new realization is not exactly the same than the previous one, this means that the new
realization differs from the previous one
'''
def add_realization_for_interval_event(feature_name , new_realization, new_realization_date, sensitive_array_attributes):
	if feature_name not in last_realization_val.keys() or feature_name not in last_realization_key.keys():
		#it is the first realization of that feature
		key = new_realization_date+"->"+new_realization_date
		value = new_realization
		
		clean_data[feature_name]={}
		clean_data[feature_name][key]=value
		last_realization_val[feature_name] = value
		last_realization_key [feature_name] = key
		
		time_variances[feature_name] = {}
		
	
	else :	

		non_sensitive_to_change_attributes = [attribute for attribute in new_realization.keys() if isinstance(new_realization[attribute], list) and attribute not in sensitive_array_attributes]
		sensitive_to_change_attributes = list(set(new_realization.keys()) - set(non_sensitive_to_change_attributes))
		#compute the duration in minutes of time we spent without having any information about the cureent feature
		missing_information_time = int(datetime.timedelta(milliseconds=(abs(long(new_realization_date.split(' , ')[1]) - long((last_realization_key[feature_name].split('->')[1]).split(' , ')[1])))).seconds/60)
		if are_equivalent(last_realization_val[feature_name], new_realization, sensitive_to_change_attributes) and missing_information_time<timeout_in_minutes:
			#the new_realization is merged with the last one (we take the merged_realization).
			#we need to extend the key so that it considers the new date
			merged_realization = merge_realizations(last_realization_val[feature_name], new_realization, non_sensitive_to_change_attributes)
			del(clean_data[feature_name][last_realization_key[feature_name]])
			last_begin_date = last_realization_key[feature_name].split('->')[0]
			last_end_date = last_realization_key[feature_name].split('->')[1]
			new_key = ""
			if new_realization_date>=last_end_date:
				#the normal case: the current occurence occured after the previous one
				new_key = last_begin_date+"->"+new_realization_date
				
				#compute the time difference between the last realization and the new one
				delta_time =int(datetime.timedelta(milliseconds=(long(new_realization_date.split(' , ')[1]) - long((last_realization_key[feature_name].split('->')[1]).split(' , ')[1]))).seconds/60)
				if delta_time not in time_variances[feature_name].keys():
					time_variances[feature_name][delta_time]=0
				time_variances[feature_name][delta_time]+=1
			
			elif new_realization_date<=last_begin_date:
				#the current realization occured even before of the beginning of the previous one
				new_key = new_realization_date+"->"+last_end_date
			
			elif new_realization_date>last_begin_date and new_realization_date<last_end_date:
				#the current realization occured in the time range of the previous one. So no key change
				new_key = last_realization_key[feature_name]
			
			
			clean_data[feature_name][new_key]=merged_realization
			last_realization_key[feature_name]=new_key
			last_realization_val[feature_name]=merged_realization
			
			
			
			
			
		else:
			#a new realization must be added
			key = new_realization_date+"->"+new_realization_date
			value = new_realization
		
			clean_data[feature_name][key]=value
			last_realization_val[feature_name] = value
			last_realization_key [feature_name] = key
			
'''
add a punctual realization to the cleaned data
'''			
def add_realization_for_ponctual_event(feature_name , new_realization, new_realization_date):
	if feature_name not in clean_data.keys():
		clean_data[feature_name]={}
	clean_data[feature_name][new_realization_date]=new_realization		
			
def get_date_key(value):
	try:
		return str(value['rcreateDateTimeZone'])+" , "+str(value['createDateTimeZone'])
	except TypeError:
		return str(value[0]['rcreateDateTimeZone'])+" , "+str(value[0]['createDateTimeZone'])
	

'''
add the attributes that are common to all the features which are:
event: the event the caused this record to be recorded
and changed: the attributes that changed since the last realization
'''	
def add_common_attributes(realization, event_type):
	realization['event']=[event_type]
	realization['changed']= []
	
	return realization
	
'''
the sensitive_to_change_attributes are the attributes that will cause the generation of a new realization when their value change.
They are represented as scalars

the non_sensitive_to_change_attributes are the attributes that their change will not cause a creation of a new realization.
they are represented as an array
'''	
def add_attributes(sensitive_to_change_attributes, non_sensitive_to_change_attributes, value, event_type, do_add_common_attributes):
	realization = {}
	if isinstance(sensitive_to_change_attributes, str) and sensitive_to_change_attributes == "-all":
		#all the attributes are sensitive to change except seq createDate, rcreateDate, createDateTimeZone, rcreateDateTimeZone
		sensitive_to_change_attributes = value.keys()
		sensitive_to_change_attributes = list(set(sensitive_to_change_attributes) - set(['seq', 'createDate', 'rcreateDate', 'createDateTimeZone', 'rcreateDateTimeZone']))
		
	for attribute in sensitive_to_change_attributes:
		realization[attribute]=value[attribute]
		
	for attribute in non_sensitive_to_change_attributes:
		realization[attribute]=[value[attribute]]
		
	if do_add_common_attributes:
		realization = add_common_attributes(realization, event_type)
		
	return realization
	
	
def add_realization_for_interval_array_event(feature_name, non_cleaned_format_new_realization, event_type, new_realization_date, sensitive_to_change_attributes, non_sensitive_to_change_attributes):
	#from the given_non_cleaned_realization, build a new realization with the cleaned version format that do not contain duplicates
	cleaned_format_new_realization = []
	for non_cleaned_entry in non_cleaned_format_new_realization:
		cleaned_entry = add_attributes(sensitive_to_change_attributes,non_sensitive_to_change_attributes, non_cleaned_entry, event_type, True)
		if not contains_equivalent_entry (cleaned_format_new_realization, cleaned_entry, sensitive_to_change_attributes):
			cleaned_format_new_realization.append(cleaned_entry)
	
	
	if feature_name not in last_realization_key.keys() or feature_name not in last_realization_val.keys():
		#first time that we see this feature
		key = new_realization_date+"->"+new_realization_date
		
		clean_data[feature_name]={}
		clean_data[feature_name][key]=cleaned_format_new_realization
		last_realization_val[feature_name] = cleaned_format_new_realization
		last_realization_key [feature_name] = key	
		
		time_variances[feature_name] = {}
		
		
	else :
		#it is not the first time that we see this feature
		is_same = True
		last_val =  last_realization_val[feature_name]
		last_key = last_realization_key[feature_name]
		
		#for each new cleaned entry, if we find one equivalent one in the previous realization then we merge both of them
		#if for every cleaned entry we found an equivalent one in the previous realizations, then the two realizations are the same
		merged_realization = []
		for cleaned_entry in cleaned_format_new_realization:
			is_found = False
			
			for old_entry in last_val:
				if are_equivalent(old_entry, cleaned_entry, sensitive_to_change_attributes) and not is_found:
					merged_realization.append(merge_realizations(old_entry, cleaned_entry, non_sensitive_to_change_attributes))
					is_found=True
					break
			if not is_found or len(last_val)!=len(cleaned_format_new_realization):
				is_same=False
		
		#compute the duration in minutes of time we spent without having any information about the cureent feature
		missing_information_time = int(datetime.timedelta(milliseconds=(abs(long(new_realization_date.split(' , ')[1]) - long((last_realization_key[feature_name].split('->')[1]).split(' , ')[1])))).seconds/60)
		if is_same and missing_information_time<timeout_in_minutes:
			#the new_realization is merged with the last one (we take the merged_realization).
			#we need to extend the key so that it considers the new date
			del(clean_data[feature_name][last_key])
			last_begin_date = last_realization_key[feature_name].split('->')[0]
			last_end_date = last_realization_key[feature_name].split('->')[1]
			new_key = ""
			if new_realization_date>=last_end_date:
				#the normal case: the current occurence occured after the previous one
				new_key = last_begin_date+"->"+new_realization_date
				
				#compute the time difference between the last realization and the new one
				delta_time =int(datetime.timedelta(milliseconds=(long(new_realization_date.split(' , ')[1]) - long((last_realization_key[feature_name].split('->')[1]).split(' , ')[1]))).seconds/60)
				if delta_time not in time_variances[feature_name].keys():
					time_variances[feature_name][delta_time]=0
				time_variances[feature_name][delta_time]+=1
				
				
				
			
			elif new_realization_date<=last_begin_date:
				#the current realization occured even before of the beginning of the previous one
				new_key = new_realization_date+"->"+last_end_date
				
				
			
			elif new_realization_date>last_begin_date and new_realization_date<last_end_date:
				#the current realization occured in the time range of the previous one. So no key change
				new_key = last_realization_key[feature_name]
			
			clean_data[feature_name][new_key]=merged_realization
			last_realization_key[feature_name]=new_key
			last_realization_val[feature_name]=merged_realization
			
			
		else:
			#a new realization must be added
			key = new_realization_date+"->"+new_realization_date
			value = cleaned_format_new_realization
		
			clean_data[feature_name][key]=value
			last_realization_val[feature_name] = value
			last_realization_key [feature_name] = key
			
	
def add_realization_for_ponctual_event_array_event(feature_name, new_realization, event_type, new_realization_date):
		new_rea=[]
		for entry in new_realization:
			entry = add_common_attributes(entry, event_type)
			new_rea.append(entry)
			
			
		if feature_name not in clean_data.keys():
			clean_data[feature_name]= {}
	
		clean_data[feature_name][new_realization_date] = new_rea
			
		
		

'''
two realizations are equivalent if the value of their sensitive to change attributes are the same
'''
def are_equivalent(realization_one, realization_two, sensitive_to_change_attributes):	
	is_equivalent = True
	
	for sen_attr in sensitive_to_change_attributes:
		if realization_one[sen_attr]!=realization_two[sen_attr]:
			is_equivalent = False
			
			
	return is_equivalent
	
	

def merge_realizations(realization_one, realization_two, non_sensitive_to_change_attributes):
	merged_realization = {}
	
	if 'event' not in non_sensitive_to_change_attributes:
		non_sensitive_to_change_attributes.append('event')
	if 'changed' not in non_sensitive_to_change_attributes:
		non_sensitive_to_change_attributes.append('changed')
	
	
	for attribute in realization_one.keys():
		if attribute in non_sensitive_to_change_attributes:
			merged_realization[attribute] = realization_one[attribute]+realization_two[attribute]
		elif realization_one[attribute]==realization_two[attribute]:
			merged_realization[attribute]= realization_one[attribute]
		else:
			#throw an exception
			raise Exception("Merge of non equivalent entries impossible")
		
	return merged_realization
	
	
def do_sanity_check (filtered_notif_data, clean_data):
	print "doing sanity check\n"
	nbr_entries_per_feature_filtered_data = {}
	nbr_entries_filtered_data = 0
	nbr_records_filtered_data=0
	for record_id in filtered_notif_data:
		for feature_name, val in filtered_notif_data[record_id].iteritems():
			if feature_name not in blacklisted_features:
				nbr_entries_filtered_data+=1
				
				if feature_name not in nbr_entries_per_feature_filtered_data.keys():
					nbr_entries_per_feature_filtered_data[feature_name]=0
				
				nbr_entries_per_feature_filtered_data[feature_name] +=1	
				
		
		nbr_records_filtered_data +=1
		
	nbr_entries_per_feature_clean_data={}
	nbr_records_clean_data = 0
	for feature, realizations in clean_data.iteritems():
		if feature not in splitted_features:
			if feature not in nbr_entries_per_feature_clean_data:
				nbr_entries_per_feature_clean_data[feature]=0
			
			for date, realization in realizations.iteritems():
				try:
					nbr_entries_per_feature_clean_data[feature]+=len(realization['event'])
						
				except TypeError:
	
					nbr_entries_per_feature_clean_data[feature]+=len(realization[0]['event'])
			
			if feature == "event":
				nbr_records_clean_data = len(realizations)
			
			
	#start the sanity check comparaison
	sanity_succeeded = False
	
	if nbr_records_clean_data == nbr_records_filtered_data:
		#second test succeded: the number of records is the same between the two versions of the data
		sanity_succeeded = True
	
	
	if sanity_succeeded:
		
		print ("The time distribution between two realizations for each feature")
		pp.pprint(time_variances)
		print ("\n\n")
		print "sanity check successful \n"
		print ("\n\n")
		
	else :
		print ("number of records in the original filtered data : "+
				str(nbr_records_filtered_data)+"\n"+"number of records in the transformed clean data (using event feature) : "+
				str(nbr_records_clean_data)+"\n\n\n")
		
		print("number of entries per feature filtered data \n")
		pp.pprint(nbr_entries_per_feature_filtered_data)
		print("\n\n")
		print ("number of entries per feature clean data \n")
		pp.pprint(nbr_entries_per_feature_clean_data)
		print("\n\n")
		print ("The time distribution between two realizations for each feature")
		print ("\n")
		pp.pprint(time_variances)
		print ("\n\n")
		print ("problem in sanity check")
		print ("\n\n")
		
	return sanity_succeeded
	
	
def order_data():
	for feature_name, dates in clean_data.iteritems():
		clean_data[feature_name] = collections.OrderedDict(sorted(dates.items()))
		
def contains_equivalent_entry (array_of_entries, entry, sensitive_to_change_attributes):
	for elem in array_of_entries:
		if are_equivalent(elem, entry, sensitive_to_change_attributes):
			return True
			
	return False
	
	
def to_str_compatible_with_equivalence(value, sensitive_to_change_attributes):
	str_representation = ""
	for attribute in sensitive_to_change_attributes :
		str_representation +=str(value[attribute])
		
	return str_representation
			
		