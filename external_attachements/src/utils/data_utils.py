
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import json
import collections
from json_utils import JsonUtils

'''
DataExtractor is the class that handles all the data extraction operations
'''
class DataExtractor:
	test_user_id = 7
	user_long_ids = {1: 358240050409564,
	2:351680061098293,
	3:357662053603904,
	4:352136065024396,
	5:359801050338118,
	6:357662053135337,
	7:352136065015162}
	json_data_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/"
	#json_data_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/20150205_json/"
	#json_data_dir = "/speech/dbwork/mul/students/dehajjik/notifications_filtered/"
	
	json_user_data_suffix = "/all/all_in_one_validated_log.json"
	
	#the 7th user is just for testing. Only called by the test methods
	user_json_path={1:json_data_dir+str(user_long_ids[1])+json_user_data_suffix,
	2: json_data_dir+str(user_long_ids[2])+json_user_data_suffix,
	3: json_data_dir+str(user_long_ids[3])+json_user_data_suffix,
	4: json_data_dir+str(user_long_ids[4])+json_user_data_suffix,
	5: json_data_dir+str(user_long_ids[5])+json_user_data_suffix,
	6: json_data_dir+str(user_long_ids[6])+json_user_data_suffix,
	7: json_data_dir+str(352136065015162)+"/all/all_in_one_log.json"}
	
	'''
	returns the json loaded data for the specified user
	'''
	@staticmethod
	def load_json_data(user_id):
		data = JsonUtils.load_json_data(DataExtractor.user_json_path[user_id])
		
		return data['logInfo']
		#return data
		
	'''
	return the all the users' id's as a list of integer
	'''
	@staticmethod
	def users_ids_list():
		return DataExtractor.user_long_ids.keys()[0:6]
	
	'''
	get the date of a record (day, month, year)
	returns a datetime.date object
	'''
	@staticmethod
	def date_of_record(record):
		'''get the date of the first feature of any record. Note that the times of the different
		note that the date of the different features of the same record are close so we decided arbitrarily 
		to take the date of the first one'''
		try:
			current_time = record.iteritems().next()[1][u'createDate']
		except TypeError:
			#in some cases the first feature is an array of features
			current_time = record.iteritems().next()[1][0][u'createDate']
		
		return datetime.date.fromtimestamp((current_time/1000.0))
	
	'''
	note that the time zone of the user is not taken into account
	'''
	@staticmethod
	def date_time_of_record(record):
		'''get the time of the first feature of any record. Note that the times of the different
		note that the time of the different features of the same record are close so we decided arbitrarily 
		to take the time of the first one'''
		try:
			current_time = record.iteritems().next()[1][u'createDate']
		except TypeError:
			#in some cases the first feature is an array of features
			current_time = record.iteritems().next()[1][0][u'createDate']
		
		return datetime.datetime.fromtimestamp((current_time/1000.0))
	
	'''
	note that the time zone of the user is not taken into account
	'''
	@staticmethod	
	def date_time_of_record_in_millis(record):
		'''get the time of the first feature of any record. Note that the times of the different
		note that the time of the different features of the same record are close so we decided arbitrarily 
		to take the time of the first one'''
		try:
			current_time = record.iteritems().next()[1][u'createDate']
		except TypeError:
			#in some cases the first feature is an array of features
			current_time = record.iteritems().next()[1][0][u'createDate']
		
		return current_time
		
	'''
	note that the time zone of the user is taken into account
	'''
	@staticmethod
	def date_time_of_record_with_time_zone(record):
		'''the feature event is present in all the records'''
		current_time = DataExtractor.date_time_of_record_in_millis_with_time_zone(record)
		
		return datetime.datetime.fromtimestamp((current_time/1000.0))
	
	'''
	note that the time zone of the user is taken into account
	'''
	@staticmethod	
	def date_time_of_record_in_millis_with_time_zone(record):
		'''the feature event is present in all the records'''
		
		gmt_time = record['event'][u'createDate']
		time_zone_offset = record['event'][u'timeZoneOffset']
		current_time = gmt_time+time_zone_offset
		
		return current_time
	
	'''
	from records, will return a list of the records that occured at the given date
	date is a datetime.date object
	records is a list of records of a validated user json file
	'''
	@staticmethod
	def select_records_by_date(data, date):
		selected_records = []
		for rec_id in data:
			if DataExtractor.date_of_record(data[rec_id])==date:
				selected_records.add(data[rec_id])
		
		return selected_records
	
	'''
	from records, will return a list of the records that occured at the given date in a given hour
	date is a datetime.datetime object
	data is in the form of validated json data
	'''
	@staticmethod	
	def select_records_by_date_and_hour(data, datetime):
		selected_records = []
		for rec_id in data:
			if DataExtractor.date_time_of_record(data[rec_id]).strftime('%Y-%m-%d %H')==datetime.strftime('%Y-%m-%d %H'):
				selected_records.append(data[rec_id])
		
		return selected_records
	

'''
DataOpearations is a class that contains some specific methods that are used to make operations on the data.
All the methods that are used by more than one external functions for making some operation in the data are
regrouped here.
'''		
class DataOperations:
	
	# blacklisted notifications
	blacklist_notifications = [
        "com.google.android.googlequicksearchbox",
        "ginlemon.flowerfree",
        "com.gau.go.launcherex",
        "com.buzzpia.aqua.launcher.buzzhome",
        "com.sony.voyagent.mixs.launcher2",
        "com.sony.voyagent.mixs.hello01",
        "com.sony.voyagent.mixs.icongetter",
        "com.sony.voyagent.mixs.mixswidget",
        "com.sony.voyagent.mixs.packager",
        "com.sony.voyagent.mixs.rawdatalogger",
		"com.sonymobile.genericuploader"]
	
	'''
	return the string representing the feature of the data_key entry if it belongs to the target_features list and if 
	it's value is known. return None otherwise.
	
	For example if the data_value contains an unknown value for a certain feature data_key = x, then the feature x 
	will not be returned even if it belongs to the target_features.
	
	(not robust method: a little bit hard coded)
	'''
	@staticmethod
	def give_me_feature(target_features, data_key, data_value):
		key = data_key
		value = data_value
		if key == 'activityRecognitionResult':
			if value['activity'] != 'Unrecognizable motion' and 'activityRecognitionResult_activity' in target_features:
				return 'activityRecognitionResult_activity'
			if value['motion'] != 'Unnkown' and 'activityRecognitionResult_motion' in target_features:
				return 'activityRecognitionResult_motion'
			if value['carrying'] != 'unknown' and 'activityRecognitionResult_carrying' in target_features:
				return 'activityRecognitionResult_carrying'
			if value['posture'] != 'unknown' and 'activityRecognitionResult_posture' in target_features:
				return 'activityRecognitionResult_posture'
		elif key == 'androidActivityRecognitionResult' and value['activity'] != 'unknown' and 'androidActivityRecognitionResult_activity' in target_features:
			return 'androidActivityRecognitionResult_activity'
		elif key == 'battery' and value['health'] != 1 and value['health'] != 'Battery health is unknown' and 'battery_health' in target_features:
			return 'battery_health'
		elif key == 'networkInfo' and value['state'] != 'UNKNOWN' and 'networkInfo_state' in target_features:
			return 'networkInfo_state'
		elif key in target_features:
			return key
		else :
			return None
			
	
	'''
	takes as input a dictionary that has dates in a string format 'year-month-day' as key and integers as values.
	Takes also as input two datetime objects that represents two different dates.
	
	fills the dictionary with all the dates between the two given dates (given dates included) with initialising them with 
	zeros. If some dates are already contained in the dictionary, then they are not modified (neither their value)
	
	There is also the option where granularity = hours and that means that the date format should be 'year-month-day hour'
	and the fill in will in each hour between the two dates.
	'''
	@staticmethod
	def fill_in_between_with_zeros(dates_dic, date_one, date_two, granularity):
		if granularity == 'hours' :
			#add all the missing days between two dates
			date_one_str = date_one.strftime('%Y-%m-%d %H')
			date_two_str = date_two.strftime('%Y-%m-%d %H')
		
			while date_one_str != date_two_str:
				if date_one_str not in dates_dic:
					dates_dic[date_one_str]=0
			
				if date_one < date_two:
					date_one += datetime.timedelta(hours=1)
					date_one_str = date_one.strftime('%Y-%m-%d %H')
				elif date_one > date_two:
					date_one -= datetime.timedelta(days=1)
					date_one_str = date_one.strftime('%Y-%m-%d %H')
		
		
			if date_two_str not in dates_dic:
				dates_dic[date_two_str]=0
		
			#useless just for clarity
			if date_one_str not in dates_dic:
				dates_dic[date_one_str]=0
		
		else :
			#granularity is days
			#add all the missing days between two dates
			date_one_str = date_one.strftime('%Y-%m-%d')
			date_two_str = date_two.strftime('%Y-%m-%d')
		
			while date_one_str != date_two_str:
				if date_one_str not in dates_dic:
					dates_dic[date_one_str]=0
			
				if date_one < date_two:
					date_one += datetime.timedelta(days=1)
					date_one_str = date_one.strftime('%Y-%m-%d')
				elif date_one > date_two:
					date_one -= datetime.timedelta(days=1)
					date_one_str = date_one.strftime('%Y-%m-%d')
		
		
			if date_two_str not in dates_dic:
				dates_dic[date_two_str]=0
		
			#useless just for clarity
			if date_one_str not in dates_dic:
				dates_dic[date_one_str]=0
		
		return dates_dic
		
	'''
	computes the number of records for some features by hour in a given period for a given json data.
	Input:
	start_time: a datetime object representing the start date and hour of the period
	end_time: a datetime object the end date and the hour of the period
	data: a json data in the validated form
	target_features: a list of strings representing the features' names that we want to plot
	
	retrun a dictionary representing the number of times each feature occured in the data by hour and date since start_time
	until end_time.
	It has the following format: {feature_name: {year-month-day hour2: number of records,
												 year-month-day hour2: number of records,
												 ...}
								}
								  {feature_name: {...
													}
								}
	
	
	'''
	@staticmethod
	def features_per_hour(start_time,end_time,data,target_features):
		features_per_hour = {}
		
		#initialize the dictionary
		for feature in target_features:
			features_per_hour[feature]={}
		
		for record_id in data:
			record = data[record_id]
			current_time = DataExtractor.date_time_of_record(record)
			
			#if the time lies between the start_time and the end_time, treat the record
			if current_time>=start_time and current_time<=end_time:
				for key, value in record.iteritems():
					feature =  DataOperations.give_me_feature(target_features, key,value)
					current_time_str = current_time.strftime('%Y-%m-%d %H')
					if feature != None:
						if current_time_str not in features_per_hour[feature]:
							features_per_hour[feature][current_time_str]=0
						
						features_per_hour[feature][current_time_str]+=1
							
		
							
		for feature, counter in features_per_hour.iteritems():
			features_per_hour[feature]= DataOperations.fill_in_between_with_zeros(counter, start_time, end_time, 'hours')
			#sort the dictionary by increasing dates
			features_per_hour[feature] = collections.OrderedDict(sorted(counter.items()))
			
		return features_per_hour
		
	'''
	order in the chronological order a list of records. 
	records = [record1, record2, ...]
	
	will return the list sorted by chronological order
	'''
	@staticmethod
	def order_chronologically(records):
		#first need to sort the records by chronological order
		records_dated = {}
		for rec in records:
			records_dated[DataExtractor.date_time_of_record(rec).strftime('%Y-%m-%d %H:%M:%S')] = rec
		
		records_dated = collections.OrderedDict(sorted(records_dated.items()))
		return records_dated.values()
		
	'''
	The same as order_chronologically
	
	will return a dictionary where each record has an annotation about his date in the form 
	year-month-day hour:minute:second
	the dictionary has the following form orderer_record = {2014-07-01 23:12:20 : record ... }
	Note that the annotation do not take into account the time zone
	'''
	@staticmethod
	def order_chronologically_and_annotate(records):
		#need to sort the records by chronological order
		records_dated = {}
		for rec in records:
			records_dated[DataExtractor.date_time_of_record(rec).strftime('%Y-%m-%d %H:%M:%S')+" , "+str(DataExtractor.date_time_of_record_in_millis(rec))] = rec
		
		records_dated = collections.OrderedDict(sorted(records_dated.items()))
		return records_dated
		
		
	'''
	The same as order_chronologically
	
	will return a dictionary where each record has an annotation about his date in the form 
	year-month-day hour:minute:second
	the dictionary has the following form orderer_record = {2014-07-01 23:12:20 : record ... }
	Note that the annotation takes into account the time zone of the user
	'''
	@staticmethod
	def order_chronologically_and_annotate_with_time_zone(records):
		#need to sort the records by chronological order
		records_dated = {}
		for rec in records:
			records_dated[DataExtractor.date_time_of_record_with_time_zone(rec).strftime('%Y-%m-%d %H:%M:%S')+" , "+str(DataExtractor.date_time_of_record_in_millis_with_time_zone(rec))] = rec
		
		records_dated = collections.OrderedDict(sorted(records_dated.items()))
		return records_dated
		
	
	
	@staticmethod
	def annotate(records):
		
		records_dated = {}
		for rec in records:
			records_dated[DataExtractor.date_time_of_record(rec).strftime('%Y-%m-%d %H:%M:%S')] = rec
		
		return records_dated
		
	
	
	
	'''
	for each feature of the record will add an entry rcreateDate (for readably create date) that will contain the
	createDate entry converted into a humanly readable date. The format of the date is the following year-month-day hour:minute:second.
	Note that the time zone is not taken into account here.
	'''	
	@staticmethod
	def annotate_with_readable_date_no_timezone(record):
		for key, value in record.iteritems():	
			try:
				current_time = value[u'createDate']
				value[u'rcreateDate'] = datetime.datetime.fromtimestamp((current_time/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
			except TypeError:
				#in some cases the first feature is an array of features
				for elem in value:
					current_time = elem[u'createDate']
					elem[u'rcreateDate'] = datetime.datetime.fromtimestamp((current_time/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
		return record
		
	
	'''
	for each feature of the record will add an entry rcreateDate (for readably create date) that will contain the
	createDate entry converted into a humanly readable date. The format of the date is the following year-month-day hour:minute:second.
	Also an entry createDateTimeZone is added and contains the time in milliseconds in POSIX with taking into account the time zone.
	An entry rcreateDateTimeZone is added and contains the humanely readable value of createDateTimeZone
	Note that the time zone is taken into account here.
	'''	
	@staticmethod
	def annotate_with_readable_date_with_timezone(record):
		time_zone_offset = record['event']['timeZoneOffset']
		for key, value in record.iteritems():	
			try:
				current_time = value[u'createDate']
				value[u'rcreateDate'] = datetime.datetime.fromtimestamp((current_time/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
				value[u'createDateTimeZone'] = current_time+time_zone_offset
				value[u'rcreateDateTimeZone'] = datetime.datetime.fromtimestamp(((current_time+time_zone_offset)/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
			except TypeError:
				#in some cases the first feature is an array of features
				for elem in value:
					current_time = elem[u'createDate']
					elem[u'rcreateDate'] = datetime.datetime.fromtimestamp((current_time/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
					elem[u'createDateTimeZone'] = current_time+time_zone_offset
					elem[u'rcreateDateTimeZone'] = datetime.datetime.fromtimestamp(((current_time+time_zone_offset)/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
		return record
	
	'''
	For the notifications array, will order it chronologically following the postTime entry.
	This postTime entry represents the time where the notification was issued.
	
	Will also add an entry rpostTime which represents the humanly readable format of postTime. 
	The format is year-month-day hour:minute:second.
	Note that the time zone is taken into account
	'''		
	@staticmethod
	def order_chronologically_notifications_and_annotate_with_timezone(record):
		time_zone_offset = record['event']['timeZoneOffset']
		if 'notifications' in record.keys():
			notifications = record['notifications']
			dated_notif = {}
			for notification in notifications:
				notification[u'rpostTime'] = datetime.datetime.fromtimestamp((notification[u'postTime']/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
				notification[u'postTimeTimeZone'] = notification[u'postTime']+time_zone_offset
				notification[u'rpostTimeTimeZone'] = datetime.datetime.fromtimestamp(((notification[u'postTime']+time_zone_offset)/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
				dated_notif[notification[u'postTime']]=notification

			dated_notif = collections.OrderedDict(sorted(dated_notif.items()))
		
			record['notifications'] = dated_notif.values()
		
		return record
		
	'''
	For the notifications array, will order it chronologically following the postTime entry.
	This postTime entry represents the time where the notification was issued.
	
	Will also add an entry rpostTime which represents the humanly readable format of postTime. 
	The format is year-month-day hour:minute:second.
	Note that the time zone is not taken into account
	'''		
	@staticmethod
	def order_chronologically_notifications_and_annotate(record):
		if 'notifications' in record.keys():
			notifications = record['notifications']
			dated_notif = {}
			for notification in notifications:
				notification[u'rpostTime'] = datetime.datetime.fromtimestamp((notification[u'postTime']/1000.0)).strftime('%Y-%m-%d %H:%M:%S')
				dated_notif[notification[u'postTime']]=notification

			dated_notif = collections.OrderedDict(sorted(dated_notif.items()))
		
			record['notifications'] = dated_notif.values()
		
		return record
	
	'''
	From the given data see the different types of notifications (different names) and their number of occurrences.
	
	returns a dictionary where the keys are the notification package name and the values the number of occurrences
	of that notification for the specified data. The dictionary is ordered so that the most frequent notifications 
	come at first and the less frequents at the end.
	
	data needs to have the following for {record_id: record1,
										record_id2: record2,...
										}
	'''	
	@staticmethod	
	def get_notification_names_count (data):
		notifications_list = {}
		for record_id in data:
			record = data[record_id]
			
			if 'notifications' in record.keys():
				notifications = record['notifications']
				for notif in notifications:
					notif_name = notif['packageName']
				
					if notif_name not in notifications_list.keys():
						notifications_list[notif_name] = 0
				
					notifications_list[notif_name]+=1
		
		notifications_list = collections.OrderedDict(sorted(notifications_list.items(), key = lambda t: t[1],reverse=True))
		return notifications_list
		
		
	'''
	From the given data see the different types of notifications (different names) and their number of occurrences.
	
	returns a dictionary where the keys are the notification package name and the values the number of occurrences
	of that notification for the specified data. The dictionary is ordered so that the most frequent notifications 
	come at first and the less frequents at the end.
	
	data needs to have the following for {record_id: record1,
										record_id2: record2,...
										}
	'''	
	@staticmethod	
	def get_notification_names_count_and_priority (data):
		notifications_list = {}
		for record_id in data:
			record = data[record_id]
			
			if 'notifications' in record.keys():
				notifications = record['notifications']
				for notif in notifications:
					notif_name = notif['packageName']
				
					if notif_name not in notifications_list.keys():
						notifications_list[notif_name] = collections.Counter()
						notifications_list[notif_name]['records'] = 0
						notifications_list[notif_name]['min_priority'] = 0
						notifications_list[notif_name]['low_priority'] = 0
						notifications_list[notif_name]['default_priority'] = 0
						notifications_list[notif_name]['high_priority'] = 0
						notifications_list[notif_name]['max_priority'] = 0
				
					notifications_list[notif_name]['records']+=1
					priority = notif['priority']
					if priority == -2:
						notifications_list[notif_name]['min_priority']+=1
					elif priority == -1:
						notifications_list[notif_name]['low_priority']+=1
					elif priority == 0:
						notifications_list[notif_name]['default_priority']+=1
					elif priority == 1:
						notifications_list[notif_name]['high_priority']+=1
					elif priority == -1:
						notifications_list[notif_name]['max_priority']+=1
		
		notifications_list = collections.OrderedDict(sorted(notifications_list.items(), key = lambda t: t[1]['records'],reverse=True))
		return notifications_list
	
		
	'''
	From the given data see the different types of events (different names) and their number of occurrences.
	
	returns a dictionary where the keys are the events names and the values the number of occurrences
	of that event for the specified data. The dictionary is ordered so that the most frequent notifications 
	come at first and the less frequents at the end.
	
	data needs to have the following for {record_id: record1,
										record_id2: record2,...
										}
	'''	
	@staticmethod	
	def get_event_types_count (data):
		events_list = {}
		for record_id in data:
			record = data[record_id]
			
			if 'event' in record.keys():
				event_name = record['event']['type']
				
				if event_name not in events_list.keys():
					events_list[event_name] = 0
				
				events_list[event_name]+=1
		
		events_list = collections.OrderedDict(sorted(events_list.items(),key = lambda t: t[1],reverse=True))
		return events_list
		
		
	
	'''
	Take a data as input an filter the useless notifications

	The filtering is done based on the following criterion:
	- some notifications is simply blacklisted because they correspond to some internal sony apps and thus not relevant for us
	- the notifications with a low priority are removed because they are not seen by the user
	- some redundant notifications will be collapsed into one. redundant notifications means the successive records that have the same notifications 
	that is just repeated in an interval of less than 5 seconds
	
	in the event feature, the event duplicated_notification is added to signal that a record has been generated due to a duplicate notification
	
	return a filtered notifications and sorted records by time of appearance in the following format:
	{2014-07-01 23:12:20 : record ... }

	'''
	@staticmethod	
	def filter_notifications (data):
		#first thing to do is to order the records and the notifications chronologically
		records = []
		for record_id in data:
			record = data[record_id]
			record = DataOperations.annotate_with_readable_date_with_timezone(record)
			record = DataOperations.order_chronologically_notifications_and_annotate_with_timezone(record)
			records.append(record)
		
		data = DataOperations.order_chronologically_and_annotate_with_time_zone(records)	
		
		#the data is chronologically sorted, we can begin the notification filtering
		last_notifications_posttimes = {}
		for record_id in data:
			record = data[record_id]
			if record['event']['type']=='notification':
				#sometimes it may occur that the event is notification and that we do not have a notification feature
				#it may be due to a problem of the record of the notification or maybe to a notification removal
				if 'notifications' in record.keys():
					#remove the blacklisted notifications, the ones with low_priority (not seen by the user) and the redundant ones
					notifications = record['notifications']
					filtered_notifications =[]
					for notif in notifications:
						#if it belongs to the blacklisted notifications remove it
						#if it has a low priority remove it
						if notif['packageName'] not in DataOperations.blacklist_notifications and notif['priority']>=0:
							#if the post time of the last notification of the same kind occurred less than 5 seconds ago
							#we consider it as a duplicate and we remove it
							if notif['packageName'] in last_notifications_posttimes.keys():
								last_post_delta = ((notif['postTime']-last_notifications_posttimes[notif['packageName']]))/1000.0
								if last_post_delta>5:
									#means that it is not a duplicate
									filtered_notifications.append(notif)
								
								#if the posttime of the current notification is newer than the previous posttime, update with the new posttime
								if notif['postTime']>last_notifications_posttimes[notif['packageName']]:
									last_notifications_posttimes[notif['packageName']]=notif['postTime']
							else:
								#it is the first time that this notification is seen so it is not a duplicate. Thus we don't remove it.
								filtered_notifications.append(notif)
								last_notifications_posttimes[notif['packageName']]=notif['postTime']
					
					if len(filtered_notifications)>0:
						record['notifications']=filtered_notifications
					else:
						#all the notifications were removed, so remove the notification feature and put for the event: duplicated_notification
						del record['notifications']
						record['event']['type']='duplicated_notification'
						
			
			else:
				#this is not a notification event so remove the notification feature from the record
				if 'notifications' in record.keys(): 
					del record['notifications']
			#put the filtered record in the place of the old one
			data[record_id] = record
			
			
		return data
		
	
	'''
	This method replaces the sequence numbers by the good values.
	it ensures that the following properties are verified:
		1- each record has a unique sequence id
		2- all the features that compose a record have all the same sequence_id
		3- if record1 appears after a record2, then sequence_id of recrod1 > sequence_id of record2
	NB: this guarantee that records are ordered by sequence number but not the features inside the sequence. In particular
	it may happen that a feature that occured in a record has a different time than the record and thus two records r1 and r2
	such that r1 appeared before r2 does not guarantee that all the features in r1 appreared before r2
	'''
	@staticmethod	
	def clean_sequence_number(data):
		# sorting the data will ensure "if record1 appears after a record2, then sequence_id of recrod1 > sequence_id of record2"
		data = collections.OrderedDict(sorted(data.items()))
		seq_number = 1
		
		for record_id in data:
			record = data[record_id]
			for feature, value in record.iteritems():
				#ensure "all the features that compose a record have all the same sequence_id"
				try:
					record[feature]["seq"]= seq_number
				except TypeError:
					for element in record[feature]:
						element["seq"] = seq_number
			#ensure "each record has a unique sequence id"
			seq_number+=1	

		#sanity check: check that the three properties are respected
		DataOperations.check_sequence_number_consistency(data)
		
		return data
			
		
		
	
	
	
	
	'''
	this method verifies that the sequence numbers in the data ensures that the following properties are verified:
		1- each record has a unique sequence id
		2- all the features that compose a record have all the same sequence_id
		3- if record1 appears after a record2, then sequence_id of recrod1 > sequence_id of record2
		
	if one of these properties is violated, then an exception will be raised
	'''
	@staticmethod
	def check_sequence_number_consistency(data):
		sorted_data_copy = collections.OrderedDict(sorted(data.items()))
		last_seq = -1
		seen_seq = []
		for record_id in sorted_data_copy:
			#Property 2 : check that all the entries has the same seq number
			record = data[record_id]
			current_seq = record['event']['seq']
			
			for feature, value in record.iteritems():
				seq = -1 
				try:
					seq = record[feature]["seq"]
				except TypeError:
					seq = record[feature][0]["seq"]
				
				if seq != current_seq:
					raise Exception("Property 2 violated: same record with different seq value")
					
			#Property 1 : check unicity of seq numbers
			if current_seq not in seen_seq:
				seen_seq.append(current_seq)
			else:
				raise Exception("Property 1 violated : sequence numbers are not unique for each record")
				
			
			#Property 3 : check that after sorting the seq values are increasing
			if current_seq>last_seq:
				last_seq = current_seq
			else:
				raise Exception("Property 3 violated : Seq values not increasing from one record to the other")
				
				
	
	'''
	See the difference of time that we have for each record between the times of the different features.
	Output a dictionary where the keys are the differences noticed and the values the number of records that had the indicated difference of time
	'''
	@staticmethod
	def test_time_variances_in_one_record(data):
		time_variances_number = {}
		time_variances_feature_min = {}
		time_variances_feature_max = {}

		for record_id in data:
			max_time = 0
			min_time = sys.maxint
			max_feature=""
			min_feature = ""
			record = data[record_id]
			
			for feature, value in record.iteritems():
				
				try:
					current_time = long(value['createDate'])
						
					if current_time > max_time :
						max_time = current_time
						max_feature = feature
					
					if current_time < min_time:
						min_time = current_time
						min_feature = feature
						
				except TypeError:
					#it is an array feature
					
					for entry in value:
						current_time = long(entry['createDate'])
						if current_time >= max_time :
							max_time = current_time
							max_feature = feature
							
						if current_time <= min_time:
							min_time = current_time
							min_feature = feature
							
							
			time_variance = max_time - min_time
			if time_variance not in time_variances_number:
				time_variances_number[time_variance] = 0
				
			time_variances_number[time_variance] +=1
			
			if max_feature not in time_variances_feature_max:
				time_variances_feature_max[max_feature] = 0
			time_variances_feature_max[max_feature] += 1
			
			if min_feature not in time_variances_feature_min:
				time_variances_feature_min[min_feature] = 0
			time_variances_feature_min[min_feature] += 1
		
		time_variances_number = collections.OrderedDict(sorted(time_variances_number.items(),reverse=True))
		
		print "time variances distribution "
		print JsonUtils.dict_as_json_str(time_variances_number)
		print "\n \n"
	

	
	@staticmethod	
	def test_time_variances_for_array_feature(data, array_feature):
		time_variances_number = {}
		time_variances_feature_min = {}
		time_variances_feature_max = {}

		for record_id in data:
			if array_feature in data[record_id]:
				max_time = 0
				min_time = sys.maxint
				feature = data[record_id][array_feature]
				for entry in feature:
					current_time = long(entry['createDate'])
					if current_time >= max_time :
						max_time = current_time
							
					if current_time <= min_time:
						min_time = current_time
			
							
				time_variance = max_time - min_time
				if time_variance not in time_variances_number:
					time_variances_number[time_variance] = 0
				
				time_variances_number[time_variance] +=1
					
		time_variances_number = collections.OrderedDict(sorted(time_variances_number.items(),reverse=True))
		
		print "time variances distribution for "+array_feature
		print JsonUtils.dict_as_json_str(time_variances_number)
		print "\n \n"
		
	
	@staticmethod	
	def print_times_for_specific_locations(data):
		accuracies = {}
		big = 0 
		small = 0
		for record_id in data:
			if "location" in data[record_id]:
				accuracy = data[record_id]["location"]["accuracy"]
				
				if accuracy not in accuracies:
					accuracies[accuracy] = 0
				
				accuracies[accuracy]+=1
				
				if accuracy>200:
					big+=1
				else:
					small+=1
					
		
		accuracies = collections.OrderedDict(sorted(accuracies.items(),reverse=True))
		print "accuracies for location are : "
		print JsonUtils.dict_as_json_str(accuracies)
		print "there is "+str(big)+" accuracies bigger than 200 meters from a total of "+str(big+small)
		print "\n \n"
	
	

