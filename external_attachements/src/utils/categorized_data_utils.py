'''
This file contains utils operations that are done on the categorized version of the data.
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
from datetime import *
import json
import collections
from json_utils import JsonUtils

'''
DataExtractor is the class that handles all the data extraction operations of the categorized version of the data
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
	
	json_data_dir = "/speech/dbwork/mul/students/dehajjik/categorized_data/"
	
	json_user_data_suffix = "/all/all_in_one_validated_log.json"
	
	#the 7th user is just for testing. Only called by the test methods
	user_json_path={1:json_data_dir+str(user_long_ids[1])+json_user_data_suffix,
	2: json_data_dir+str(user_long_ids[2])+json_user_data_suffix,
	3: json_data_dir+str(user_long_ids[3])+json_user_data_suffix,
	4: json_data_dir+str(user_long_ids[4])+json_user_data_suffix,
	5: json_data_dir+str(user_long_ids[5])+json_user_data_suffix,
	6: json_data_dir+str(user_long_ids[6])+json_user_data_suffix,
	7: json_data_dir+str(352136065015162)+json_user_data_suffix}
	
	location_name = "location"
	location_attribute = "place"
	location_metaradius = "radius"
	location_metacenter = "center"
	location_metawifi = "wifi"
	location_metastation = "station"
	location_metagps= "gps"
	
	data_id = "data"
	metadata_id = "metadata"
	

	date_format = "%Y-%m-%d"
	time_format = "%H:%M:%s"
	date_time_sep=" "
	date_time_format = date_format+date_time_sep+time_format

	
	'''
	returns the json loaded data for the specified user
	'''
	@staticmethod
	def load_json_data(user_id):
		data = JsonUtils.load_json_data(DataExtractor.user_json_path[user_id])
		return data
		
	'''
	return the all the users' id's as a list of integer
	'''
	@staticmethod
	def users_ids_list():
		return DataExtractor.user_long_ids.keys()[0:6]
		
	'''
	return the data of the indicated feature
	data is the complete data from which the extraction occurs (it contains data information and metadata information)
	'''
	@staticmethod
	def data(feature_name, data):
		return data[DataExtractor.data_id][feature_name]
		
	'''
	return the complete data of the indicated feature
	'''
	@staticmethod
	def complete_data(data):
		return data[DataExtractor.data_id]
	
	
	'''
	return the metadata of the indicated feature
	data is the data from which the extraction occurs
	'''
	@staticmethod
	def metadata(feature_name, data):
		return data[DataExtractor.metadata_id][feature_name]
		
	'''
	return the complete metadata of the indicated feature
	
	'''
	@staticmethod
	def complete_metadata(data):
		return data[DataExtractor.metadata_id]
		
	'''
	input: the key of the desired realization
	return a string object representing the starting time of the realization (date + unix millis)
	'''
	@staticmethod
	def start_complete_date_of_realization(realization_key):
		st_date_str = realization_key.split('->')[0]
		return st_date_str
		
	'''
	input: the key of the desired realization
	return a string object representing the end time of the realization (date + unix millis)
	'''
	@staticmethod
	def end_complete_date_of_realization(realization_key):
		st_date_str = realization_key.split('->')[1]
		return st_date_str
		
	'''
	input: the key of the desired realization
	return a datetime object representing the starting time of the realization
	'''
	@staticmethod
	def start_date_of_realization(realization_key):
		st_date_str = realization_key.split('->')[0].split(" , ")[0]
		return datetime.strptime(st_date_str, '%Y-%m-%d %H:%M:%S')
	'''
	input: the key of the desired realization
	return long representing the UNIX time in milliseconds of the start of the realization
	'''
	@staticmethod
	def start_date_of_realization_in_millis(realization_key):
		return float(realization_key.split('->')[0].split(" , ")[1])
		
	'''
	input: the key of the desired realization
	return a datetime object representing the end time of the realization
	'''	
	@staticmethod
	def end_date_of_realization(realization_key):
		st_date_str = realization_key.split('->')[1].split(" , ")[0]
		return datetime.strptime(st_date_str, '%Y-%m-%d %H:%M:%S')
	
	'''
	input: the key of the desired realization
	return long representing the UNIX time in milliseconds of the end of the realization
	'''
	@staticmethod
	def end_date_of_realization_in_millis(realization_key):
		return float(realization_key.split('->')[1].split(" , ")[1])
		
	'''
	input: the key of the desired realization
	return a date object representing the day the month and the year of the begin of the realization. the time is not included
	'''
	@staticmethod
	def start_date_no_time_of_realization(realization_key):
		return DataExtractor.start_date_of_realization(realization_key).date()
		
	
	'''
	input: the key of the desired realization
	return a date object representing the day the month and the year of end of the realization. the time is not included
	'''
	@staticmethod
	def end_date_no_time_of_realization(realization_key):
		return DataExtractor.end_date_of_realization(realization_key).date()
		
	'''
	input: all the realizations of one feature sorted by increasing chronological order, a time interval represented in the format of a realization_key
	
	return: the realizations that occured during the interval given
	
	We consider that a realization occured in the selected time frame under two conditions:
					1- if the time interval of the realization overlaps with the selected time frame
					2- if the time interval of the realization overlaps with the time frame of the last selected realization
				This is the soft version of the realization extraction
	'''
	@staticmethod
	def extract_realizations_in_time_range_soft_version(feature_realizations_sorted, realization_key):
			
		#print "extract the dates that overlaps with"+realization_key+"\n"
			
		target_realizations = []
		target_time_range = realization_key
			
		for current_time_range, realization in feature_realizations_sorted.iteritems():
				
			if DataOperations.does_date_overlaps(target_time_range , current_time_range):
				#the current realization has a time that overlaps with the target time so we select it and extend the target time so that it includes the time range of the selected realization (to satisfy the soft version property)
				#print current_time_range+ ": SELECTED \n"
				target_realizations.append(realization)
				target_time_range = DataOperations.union_of_date_intervals(target_time_range , current_time_range)
				
			elif DataOperations.is_ended_before_the_start_of(target_time_range , current_time_range):
				#if the current time range started after the finish of the target one, it means that we will not meet any realizations in the target time range any more
				#print current_time_range+ ": CAUSED STOP LOOP \n"
				break;
				
			
		#print "the selected realizations are \n"+JsonUtils.dict_as_json_str(target_realizations)+"\n\n\n\n"
		#print "\n\n\n\n"
		return target_realizations
		
	'''
	This method must be used under in a set of very precise conditions :
		- the realization keys that will be given as an entry must be sorted in an increasing order
		- feature_realizations_sorted_copy MUST BE A COPY of the original data so that it can be modified inside this method
		- this method impacts the running time performance if it will be called many times inside a loop
	
	input: a copy of all the realizations of one feature sorted by increasing chronological order, a time interval represented in the format of a realization_key
	
	return: the realizations that occured during the interval given
	
	We consider that a realization occured in the selected time frame under two conditions:
					1- if the time interval of the realization overlaps with the selected time frame
					2- if the time interval of the realization overlaps with the time frame of one selected realization
				This is the soft version of the realization extraction
	'''	
	@staticmethod
	def extract_realizations_in_time_range_soft_version_optimized_for_sorted_data_copy(feature_realizations_sorted_copy, realization_key):
		target_realizations = []
		target_time_range = realization_key
			
		for current_time_range in feature_realizations_sorted_copy.keys():
			realization = feature_realizations_sorted_copy[current_time_range]
			
			if DataOperations.is_ended_before_the_start_of(current_time_range, target_time_range):
				#the current realization happened before the target time, so as we assume that the target times that will be given as input to the method are increasing,
				#we just remove this entry
				del feature_realizations_sorted_copy[current_time_range]
				
			elif DataOperations.does_date_overlaps(target_time_range , current_time_range):
				#the current realization has a time that overlaps with the target time so we select it and extend the target time so that it includes the time range of the selected realization(to satisfy the soft version property)
				target_realizations.append(realization)
				#as the target times are strictly increasing, we delete this entry because it will never match another target time
				del feature_realizations_sorted_copy[current_time_range]
				target_time_range = DataOperations.union_of_date_intervals(target_time_range , current_time_range)
				
			elif DataOperations.is_ended_before_the_start_of(target_time_range , current_time_range):
				#if the current time range started after the finish of the target one, it means that we will not meet any realizations in the target time range any more
				#print current_time_range+ ": CAUSED STOP LOOP \n"
				break;
				
			
		#print "the selected realizations are \n"+JsonUtils.dict_as_json_str(target_realizations)+"\n\n\n\n"
		#print "\n\n\n\n"
		return target_realizations
	
	'''
	This method must be used under in a set of very precise conditions :
		- the realization keys that will be given as an entry must be sorted in an increasing order
		- feature_realizations_sorted_copy MUST BE A COPY of the original data so that it can be modified inside this method
		- this method impacts the running time performance if it will be called many times inside a loop
	
	input: a copy of all the realizations of one feature sorted by increasing chronological order, a time interval represented in the format of a realization_key
	
	return: the realizations that occured during the interval given
	
	We consider that a realization occured in the selected time frame under two conditions:
					1- if the time interval of the realization overlaps with the selected time frame
					2- if the time interval of the realization overlaps with the time frame of one selected realization
				This is the soft version of the realization extraction
	'''	
	@staticmethod
	def extract_realizations_in_time_range_soft_version_optimized_for_sorted_data_copy_verbose(feature_realizations_sorted_copy, realization_key):
		target_realizations = []
		target_time_range = realization_key
			
		for current_time_range in feature_realizations_sorted_copy.keys():
			realization = feature_realizations_sorted_copy[current_time_range]
			
			if DataOperations.is_ended_before_the_start_of(current_time_range, target_time_range):
				#the current realization happened before the target time, so as we assume that the target times that will be given as input to the method are increasing,
				#we just remove this entry
				del feature_realizations_sorted_copy[current_time_range]
				
			elif DataOperations.does_date_overlaps(target_time_range , current_time_range):
				#the current realization has a time that overlaps with the target time so we select it and extend the target time so that it includes the time range of the selected realization(to satisfy the soft version property)
				print "gps "+JsonUtils.dict_as_json_str(realization)+" that occured at time "+current_time_range+" included in the selection"
				target_realizations.append(realization)
				#as the target times are strictly increasing, we delete this entry because it will never match another target time
				del feature_realizations_sorted_copy[current_time_range]
				target_time_range = DataOperations.union_of_date_intervals(target_time_range , current_time_range)
				
			elif DataOperations.is_ended_before_the_start_of(target_time_range , current_time_range):
				#if the current time range started after the finish of the target one, it means that we will not meet any realizations in the target time range any more
				#print current_time_range+ ": CAUSED STOP LOOP \n"
				break;
				
			
		#print "the selected realizations are \n"+JsonUtils.dict_as_json_str(target_realizations)+"\n\n\n\n"
		#print "\n\n\n\n"
		return target_realizations
		
			
	
	'''
	input: all the realizations of one feature sorted by increasing chronological order, a time interval represented in the format of a realization_key
	
	return: the realizations that occured during the interval given
	
	We consider that a realization occured in the selected time frame onyl if the following condition is satisfied:
					1- if the time interval of the realization overlaps with the selected time frame
				This is the strict version of the realization extraction
	'''
	@staticmethod
	def extract_realizations_in_time_range_strict_version(feature_realizations_sorted, realization_key):
		
		
		target_realizations = []
		target_time_range = realization_key
			
		for current_time_range, realization in feature_realizations_sorted.iteritems():
			#if the current time range started after the finish of the target one, it means that we will not meet any realizations in the target time range any more
			if DataOperations.is_ended_before_the_start_of(target_time_range , current_time_range):
				break;
			elif DataOperations.does_date_overlaps(target_time_range , current_time_range):
				target_realizations.append(realization)
			
		return target_realizations
				
				
	
'''
DataOpearations is a class that contains some specific methods that are used to make operations on the data.
All the methods that are used by more than one external functions for making some operation in the data are
regrouped here.
'''		
class DataOperations:
	default_time = "00:00:00"
	'''
	takes a realization key and replace the times by default time
	returns the same string representation as realization with the default time replaced and the millis numbers ignored
	'''
	@staticmethod
	def build_date_with_default_time_no_millis(realization_key):
		new_start_date = DataExtractor.start_date_no_time_of_realization(realization_key).strftime(DataExtractor.date_format)+DataExtractor.date_time_sep+DataOperations.default_time
		new_end_date = DataExtractor.end_date_no_time_of_realization(realization_key).strftime(DataExtractor.date_format)+DataExtractor.date_time_sep+DataOperations.default_time
		return DataOperations.build_interval(new_start_date, new_end_date)
		
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  and the interval represented by key1 started before the interval represented by the interval 2. The precision taken into account is seconds
	'''
	@staticmethod
	def is_started_before(realization_key1 , realization_key2):
		return DataExtractor.start_date_of_realization(realization_key1)<DataExtractor.start_date_of_realization(realization_key2)
		
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  the interval represented by key1 and the interval represented by the interval 2 started at the same time.
	The precision taken into account is seconds

	'''	
	@staticmethod
	def is_same_start_time(realization_key1 , realization_key2):
		return DataExtractor.start_date_of_realization(realization_key1)==DataExtractor.start_date_of_realization(realization_key2)
	
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  and the interval represented by key1 ended before the interval represented by the interval 2.
	The precision taken into account is seconds
	'''
	@staticmethod
	def is_ended_before(realization_key1 , realization_key2):
		return DataExtractor.end_date_of_realization(realization_key1)<DataExtractor.end_date_of_realization(realization_key2)
		
	
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  the interval represented by key1 and the interval represented by the interval 2 ended at the same time.
	
	The precision taken into account is seconds
	'''	
	@staticmethod
	def is_same_end_time(realization_key1 , realization_key2):
		return DataExtractor.end_date_of_realization(realization_key1)==DataExtractor.end_date_of_realization(realization_key2)
		
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  the interval represented by key1 ends before the starting of the interval represented by the interval 2 .
	
	The precision taken into account is seconds
	'''	
	@staticmethod
	def is_ended_before_the_start_of(realization_key1 , realization_key2):
		return DataExtractor.end_date_of_realization(realization_key1)<DataExtractor.start_date_of_realization(realization_key2)
		
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  the interval represented by key1 ends at the same time than the interval represented by the interval 2 starts.
	
	The precision taken into account is seconds
	'''	
	@staticmethod
	def is_ended_at_the_start_of(realization_key1 , realization_key2):
		return DataExtractor.end_date_of_realization(realization_key1)==DataExtractor.start_date_of_realization(realization_key2)
		
	
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  and the interval represented by key1 and the interval represented by the interval 2 overlaps 
	The precision taken into account is seconds
	'''
	@staticmethod
	def does_date_overlaps(realization_key1 , realization_key2):			
		if (DataOperations.is_ended_before_the_start_of(realization_key1 , realization_key2) or DataOperations.is_ended_before_the_start_of(realization_key2 , realization_key1)):
			# the two intervals do not overlap
			return False
		else:
			return True
	
	
	'''
	the realizations keys represents start dates and end date, i.e interval of dates
	
	return true if  and the interval represented by key2 is completely contained in the interval represented by the interval 1.
	
	Note that: is_contained_in(realization_key1 , realization_key2) => does_date_overlaps(realization_key1 , realization_key2)
			   but  does_date_overlaps(realization_key1 , realization_key2) !=> is_contained_in(realization_key1 , realization_key2)
	
	The precision taken into account is seconds
	'''
	@staticmethod
	def is_contained_in(realization_key1 , realization_key2):
		if DataOperations.is_started_before(realization_key2 , realization_key1) or not (DataOperations.is_ended_before(realization_key2 , realization_key1) or DataOperations.is_same_end_time(realization_key2 , realization_key1)) :
			#the realization 2 is not completely contained in the realization 1
			return False
		else:
			return True
			
	'''
	does the union of two intervals of time.
	If they do not overlap, it just takes the minimum start time and makes it union with the maxmimum end time
	The overlapping test takes into account the seconds precision
	'''
	@staticmethod
	def union_of_date_intervals_soft_version(realization_key1 , realization_key2):
		start_time = ""
		end_time = ""
		if DataOperations.is_started_before(realization_key1 , realization_key2):
			start_time = DataExtractor.start_complete_date_of_realization(realization_key1)
		else:
			start_time = DataExtractor.start_complete_date_of_realization(realization_key2)
		
		
		if DataOperations.is_ended_before(realization_key1 , realization_key2):
			end_time = DataExtractor.end_complete_date_of_realization(realization_key2)
		else:
			end_time = DataExtractor.end_complete_date_of_realization(realization_key1)
		
		return DataOperations.build_interval(start_time, end_time)
	
	
	'''
	does the union of two intervals of time.
	
	'''
	@staticmethod
	def union_of_date_intervals(realization_key1 , realization_key2):
		if DataOperations.does_date_overlaps(realization_key1 , realization_key2):
			return DataOperations.union_of_date_intervals_soft_version(realization_key1 , realization_key2)
		else:
			raise Exception("The intervals do not overlap so their union results in two intervals, this part is not implemented. Can use the soft union version if the non overlapping part needs to be included")
	

	'''
	does the intersection of two intervals of time. returns the intersected interval in the same format than the realization keys
	If they do not overlap, retrurn None.
	The overlapping test takes into account the seconds precision
	'''
	@staticmethod
	def intersection_of_date_intervals(realization_key1 , realization_key2):
		if DataOperations.does_date_overlaps(realization_key1 , realization_key2):
			#intersection is non empty
			inter_start_time = DataExtractor.start_complete_date_of_realization(realization_key1)
			if DataOperations.is_started_before(realization_key1 , realization_key2):
				inter_start_time = DataExtractor.start_complete_date_of_realization(realization_key2)
				
			inter_end_time = DataExtractor.end_complete_date_of_realization(realization_key2)
			if DataOperations.is_ended_before(realization_key1 , realization_key2):
				inter_end_time = DataExtractor.end_complete_date_of_realization(realization_key1)
			
			return DataOperations.build_interval(inter_start_time, inter_end_time)
			
		else:
			return None
			
	
	'''
	does the intersection of two intervals of time. returns the intersected interval in the same format than the realization keys
	If they do not overlap, retrurn None. Do not care about the time it only cares about the date
	'''
	@staticmethod
	def intersection_of_date_intervals_day_precision(realization_key1 , realization_key2):
		realization_key1_date = DataOperations.build_date_with_default_time_no_millis(realization_key1)
		realization_key2_date = DataOperations.build_date_with_default_time_no_millis(realization_key2)
		
		
		if DataOperations.does_date_overlaps(realization_key1_date , realization_key2_date):
			#intersection is non empty
			inter_start_time = DataExtractor.start_complete_date_of_realization(realization_key1_date)
			if DataOperations.is_started_before(realization_key1_date , realization_key2_date):
				inter_start_time = DataExtractor.start_complete_date_of_realization(realization_key2_date)
				
			inter_end_time = DataExtractor.end_complete_date_of_realization(realization_key2_date)
			if DataOperations.is_ended_before(realization_key1_date , realization_key2_date):
				inter_end_time = DataExtractor.end_complete_date_of_realization(realization_key1_date)
			
			return DataOperations.build_interval(inter_start_time, inter_end_time)
			
		else:
			return None
			
	'''
	substract the realization2 from the realization 1.
	return the substracted interval
	
	IMOPORTANT NOTE: the substraction do not remove the element at the border, that why it is soft
	'''
	@staticmethod
	def substraction_of_date_intervals_soft_version(realization_key1 , realization_key2):
		
		if DataOperations.is_contained_in(realization_key1 , realization_key2):
			if DataOperations.is_same_start_time(realization_key1 , realization_key2):
				return DataOperations.build_interval(DataExtractor.end_complete_date_of_realization(realization_key2), DataExtractor.end_complete_date_of_realization(realization_key1))
			
			else:
				raise Exception("substraction should end up with separate intervals: Not implemented yet")
		
		else:
			raise Exception("substraction not possible: interval "+realization_key2+" is not totally contained in interval "+realization_key1)
			
			
			
	'''
	substract the realization2 from the realization 1.
	return the substracted interval
	
	IMOPORTANT NOTE: the substraction do not remove the element at the border, that why it is soft
	'''
	@staticmethod
	def substraction_of_date_intervals_soft_version_day_precision(realization_key1 , realization_key2):
		realization_key1_date = DataOperations.build_date_with_default_time_no_millis(realization_key1)
		realization_key2_date = DataOperations.build_date_with_default_time_no_millis(realization_key2)
		if DataOperations.is_contained_in(realization_key1_date , realization_key2_date):
			if DataOperations.is_same_start_time(realization_key1_date , realization_key2_date):
				return DataOperations.build_interval(DataExtractor.end_complete_date_of_realization(realization_key2_date), DataExtractor.end_complete_date_of_realization(realization_key1_date))
			
			else:
				raise Exception("substraction should end up with separate intervals: Not implemented yet")
		
		else:
			raise Exception("substraction not possible: interval "+realization_key2_date+" is not totally contained in interval "+realization_key1_date)
	
	@staticmethod	
	def build_interval(start_date, end_date):
		return start_date+"->"+end_date
		
	'''
	return the number of days covered by a time interval realization_key
	'''
	@staticmethod	
	def days(realization_key):
		start_date = DataExtractor.start_date_of_realization(realization_key)
		end_date = DataExtractor.end_date_of_realization(realization_key)
		
		days_covered = ((end_date-start_date).days)+1
		return days_covered
		

		
			
		
	
	
	

