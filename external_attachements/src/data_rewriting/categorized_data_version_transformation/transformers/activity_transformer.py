#!/usr/bin/env python
import sys
import collections
import pprint as pp
import copy
from datetime import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from clean_data_utils import *
from json_utils import JsonUtils
from gps_utils import GpsUtils
from feature_transformer import FeatureTransformer
from date_time_utils import DateTimeUtils
import math
import numpy as np
from numpy_utils import *
from plot_lib_utils import *
from clean_data_utils import *


'''
		
'''
class ActivityTransformer (FeatureTransformer):
	transformed_feature_name = "activity"
	transformed_feature_attribute = "id"
	
	intermediair_transformed_feature_activities = "ids"
	intermediair_transformed_feature_confidences = "confidences"
	
	#timeout is set to the equivalent of 30 minutes. if the same activity occurs in delta time smaller or equal to timeout, then we assume that, this activity was occuring in between
	timeout_in_millis = 1000*60*30
	
	
	sony_activity_feature = "activityRecognitionResult_main"
	sony_activity_motion = "motion"
	sony_activity_posture = "posture"
	sony_unknown_activities = ["unknown", ""]
	#sony activites names
	sony_activity_elevator_up = "elevator-up"
	sony_activity_elevator_down = "elevator-down"
	sony_activity_escalator_up = "escalator-up"
	sony_activity_escalator_down = "escalator-down"
	sony_activity_stairs_up = "stairs-up"
	sony_activity_stairs_down = "stairs-down"
	sony_activity_name_car = "car"
	sony_activity_name_train= "train"
	sony_activity_name_bus= "bus"
	sony_activity_name_bicycle= "bicycle"
	sony_activity_name_run= "run"
	sony_activity_name_walk= "walk"
	sony_activity_name_still= "still"
	sony_activity_name_jump= "jump"
	
	android_activity_feature = "androidActivityRecognitionResult_other"
	android_activity_activities = "activities"
	android_activity_confidences = "confidences"
	android_unknown_activities = ["UNKNOWN", "unknown", ""]
	
	#different target activities names
	android_activity_name_vehicle= "in_vehicle"
	android_activity_name_bicycle= "on_bicycle"
	android_activity_name_tilting= "tilting"
	android_activity_name_foot= "on_foot"
	android_activity_name_walking= "walking"
	android_activity_name_running = "running"
	android_activity_name_still= "still"
	
	
	#different target activities names
	target_activity_name_move_up_or_down = "move_up_or_down"
	target_activity_name_car = "in_car"
	target_activity_name_train= "in_train"
	target_activity_name_bus= "in_bus"
	target_activity_name_bicycle= "in_bicycle"
	target_activity_name_run= "running"
	target_activity_name_walk= "walking"
	target_activity_name_foot= "on_foot"
	target_activity_name_still= "still"
	target_activity_name_jump= "jumping"
	target_activity_name_tilting= "tilting"
	target_activity_name_vehicle= "in_vehicle"
	
	
	
	def __init__(self, nontransformed_data):
		super(ActivityTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata={}
		self.transformed_feature_data={}
		
		#maps each activity name to an id
		self.transformed_feature_reverse_metadata={}
		
		
		
		#add empty realizations if the notification feature is not present in the data
		if self.sony_activity_feature not in self.nontransformed_data:
			self.nontransformed_data[self.sony_activity_feature] = {}
			
		if self.android_activity_feature not in self.nontransformed_data:
			self.nontransformed_data[self.android_activity_feature] = {}
		
		#sort the notifications by increasing date
		print "ordering the sony activity and the android activity info by date"
		self.nontransformed_data[self.sony_activity_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.sony_activity_feature].items()))	
		self.nontransformed_data[self.android_activity_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.android_activity_feature].items()))	
	

		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		
		sony_activity_counts = self.count_sony_activity_realizations()
		android_activity_counts = self.count_android_activity_realizations()
		
		print "Sony activities duration (in minutes) :"
		print JsonUtils.dict_as_json_str(sony_activity_counts)
		
		print "Android activities duration (in minutes) : "
		print JsonUtils.dict_as_json_str(android_activity_counts)
		
		
		#self.exclusive_sony_activity_transform_one()
		self.exclusive_android_activity_transform_one()
	
	'''
	takes into account only the sony activity result and ignores the android
	
	maps the four sony activites sony_activity_elevator_up, self.sony_activity_elevator_down ,self.sony_activity_escalator_up ,self.sony_activity_escalator_down
	to a unique class target_activity_name_move_up_or_down. keeps all the other classes but with slightly different naming
	'''
	def exclusive_sony_activity_transform_one(self):	
		#map the initial activities into the target activity space
		print "creating the metadata and mapping the initial activities into a new activity space"
		self.exclusive_sony_activity_metadata_and_mapping_one()
		
		
		#transform the sony data into ids
		print "transforming the data into the categorized version"
		categorized_sony_activity = self.transform_sony_activity_feature()
		
		#merge the realizations if two same activities are close enougth
		print "concatenating the close and same activity realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(categorized_sony_activity)
		#self.transformed_feature_data = categorized_sony_activity
		
		
	
	
	def exclusive_android_activity_transform_one(self):	
		#map the initial activities into the target activity space
		print "creating the metadata and mapping the initial activities into a new activity space"
		self.exclusive_android_activity_metadata_and_mapping_one()
		
		
		#transform the sony data into ids
		print "transforming the data into the categorized version"
		intermediair_categorized_android_activity = self.transform_android_activity_feature()
		categorized_android_activity = self.intermediaire_to_final_transformer_one(intermediair_categorized_android_activity)
		
		
		#merge the realizations if two same activities are close enougth
		print "concatenating the close and same activity realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(categorized_android_activity)
		#self.transformed_feature_data = categorized_android_activity
		
	
	
	
	'''
	maps the four sony activites sony_activity_elevator_up, self.sony_activity_elevator_down ,self.sony_activity_escalator_up ,self.sony_activity_escalator_down
	to a unique class target_activity_name_move_up_or_down. keeps all the other classes but with slightly different naming
	
	it replaces all the entries by the target activities and create the metadata
	'''
	def exclusive_sony_activity_metadata_and_mapping_one(self):
		initial_to_target_activity_mapper = {self.sony_activity_feature: {  self.sony_activity_elevator_up : self.target_activity_name_move_up_or_down,
																			self.sony_activity_elevator_down : self.target_activity_name_move_up_or_down,
																			self.sony_activity_escalator_up : self.target_activity_name_move_up_or_down,
																			self.sony_activity_escalator_down : self.target_activity_name_move_up_or_down,
																			self.sony_activity_stairs_up : self.target_activity_name_move_up_or_down,
																			self.sony_activity_stairs_down : self.target_activity_name_move_up_or_down,
																			self.sony_activity_name_car : self.target_activity_name_car,
																			self.sony_activity_name_train : self.target_activity_name_train,
																			self.sony_activity_name_bus : self.target_activity_name_bus,
																			self.sony_activity_name_bicycle : self.target_activity_name_bicycle,
																			self.sony_activity_name_run : self.target_activity_name_run,
																			self.sony_activity_name_walk : self.target_activity_name_walk,
																			self.sony_activity_name_still : self.target_activity_name_still,
																			self.sony_activity_name_jump : self.target_activity_name_jump,
																		 }
		
		
											
											}
		self.map_activity_space_and_create_metadata(initial_to_target_activity_mapper)
		return initial_to_target_activity_mapper.keys()
		
		
	
	def exclusive_android_activity_metadata_and_mapping_one(self):
		initial_to_target_activity_mapper = {self.android_activity_feature: { 
																			self.android_activity_name_vehicle : self.target_activity_name_vehicle,
																			self.android_activity_name_bicycle : self.target_activity_name_bicycle,
																			self.android_activity_name_walking : self.target_activity_name_foot,
																			self.android_activity_name_foot: self.target_activity_name_foot,
																			self.android_activity_name_running: self.target_activity_name_foot,
																			self.android_activity_name_still : self.target_activity_name_still,
																			self.android_activity_name_tilting : self.target_activity_name_tilting,
																		 }
											}
											
		
		self.map_activity_space_and_create_metadata(initial_to_target_activity_mapper)
		return initial_to_target_activity_mapper.keys()
		
	
	
		
	'''
	taking into account the target activities, transforms the sony activity in the categorized way
	
	returns the categorized data
	'''
	def transform_sony_activity_feature(self):
		transformed_sony_activity = {}
		original_sony_activity = self.nontransformed_data[self.sony_activity_feature]
		
		for date, activity_info in original_sony_activity.iteritems():
			activity_id = self.transformed_feature_reverse_metadata[activity_info[self.sony_activity_motion]]
			transformed_sony_activity[date] = {self.transformed_feature_attribute : activity_id}
			
		#sort by chronological order
		transformed_sony_activity = collections.OrderedDict(sorted(transformed_sony_activity.items()))
		return transformed_sony_activity
		
	
	'''
	taking into account the target activities, transforms the android activity in an itermediair categorized way.
	intermediair because we want to keep all the confidences with the ids in this stage
	
	returns the categorized data
	'''
	def transform_android_activity_feature(self):
		transformed_android_activity = {}
		original_android_activity = self.nontransformed_data[self.android_activity_feature]
		
		for date, activity_info in original_android_activity.iteritems():
			activities_id = {self.transformed_feature_reverse_metadata[activity] for activity in activity_info[self.android_activity_activities]}
			confidences = activity_info[self.android_activity_confidences]
			
			#we may have two activities_ids that are the same in activities ids. in this case, we need to sum their confidences
			act_conf_dict = {}
			index = 0
			for activity_id in activities_id:
				if activity_id not in act_conf_dict:
					act_conf_dict[activity_id] = 0
				
				act_conf_dict[activity_id] += confidences[index]
				index +=1
			
			act_conf_dict =  collections.OrderedDict(sorted(act_conf_dict.items(), key=lambda x: x[1], reverse = True))
			
			transformed_android_activity[date] = {self.intermediair_transformed_feature_activities : act_conf_dict.keys(),
												self.intermediair_transformed_feature_confidences : act_conf_dict.values()}
				
			
		#sort by chronological order
		transformed_android_activity = collections.OrderedDict(sorted(transformed_android_activity.items()))
		return transformed_android_activity
		
		
	
	'''
	we may want to regroup some initial activities into bigger classes or to map the android activity names to the same set of the sony activity names.
	This method does this mapping by going through all the data and mapping the activities found into the target activities specified by the mapper (initial_to_target_activity_mapper).
	This method also creates the metadata using the mapper.
	
	The mapper is dict that has the following format: { activityRecognitionResult_main : {sony_activity_name_1 : target_name1 , sony_activity_name_2 : target_name2,...}
														androidActivityRecognitionResult_other : {android_activity_name_1 : target_name1 , android_activity_name_2 : target_name2,...}
													}
	
	if the mapper do not contain the key activityRecognitionResult_main, then only the android activities will be transformed. The same applies for androidActivityRecognitionResult_other.
	'''
	def map_activity_space_and_create_metadata(self, initial_to_target_activity_mapper):
		#this method also filters out away the unknown activities for both android and sony
		reverse_metadata_dict = {}
		target_activity_id = 0
		
		#map the sony activities to the target activities
		if self.sony_activity_feature in initial_to_target_activity_mapper:
			for date, activity_info in self.nontransformed_data[self.sony_activity_feature].iteritems():
				activity = activity_info[self.sony_activity_motion]
				if activity in self.sony_unknown_activities:
					raise Exception("UNSUPPORTED VALUE EXCEPTION: the is an unknown activity in Sony Recognition Activity feature. its value is: "+activity)
				
				target_activity = initial_to_target_activity_mapper[self.sony_activity_feature][activity]
				
				activity_info[self.sony_activity_motion] = target_activity
				
				if target_activity not in reverse_metadata_dict:
					reverse_metadata_dict[target_activity] = target_activity_id
					target_activity_id +=1 
			
			#sort by chronological order
			self.nontransformed_data[self.sony_activity_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.sony_activity_feature].items()))
				
		#map the android activities to the target activities
		if self.android_activity_feature in initial_to_target_activity_mapper:
			unknown_filtered_android_activity = {}
			for date, activity_info in self.nontransformed_data[self.android_activity_feature].iteritems():
				activities = activity_info[self.android_activity_activities]
				confidences = activity_info[self.android_activity_confidences]
				index = 0
				target_activities = []
				target_confidences = []
				for activity in activities:
					
					if activity not in self.android_unknown_activities:
						
						target_activity = initial_to_target_activity_mapper[self.android_activity_feature][activity]
						target_activities.append(target_activity)
						target_confidences.append(confidences[index])
						
						
						#update the metadata dict
						if target_activity not in reverse_metadata_dict:
							reverse_metadata_dict[target_activity] = target_activity_id
							target_activity_id +=1 
					
					index +=1
				
				activity_info[self.android_activity_activities] = target_activities
				activity_info[self.android_activity_confidences] = target_confidences
				
				
				
				if len(target_activities) > 0:
					unknown_filtered_android_activity[date] = activity_info
					
				if len(target_activities) != len(target_confidences):
					raise Exception("UNEXPECTED BEHAVIOUR EXCEPTION: the confidences array and the activites array do not have the same length")
						
			self.nontransformed_data[self.android_activity_feature] = unknown_filtered_android_activity
			
			#sort by chronological order
			self.nontransformed_data[self.android_activity_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.android_activity_feature].items()))	
			
		#save the metadata in the class variable. Note that we invert the keys and the values so that we have the ids as keys and the activity names as values
		self.transformed_feature_metadata[self.transformed_feature_attribute]= dict (zip(reverse_metadata_dict.values(),reverse_metadata_dict.keys()))
		
		self.transformed_feature_reverse_metadata=reverse_metadata_dict
		
	

	def intermediaire_to_final_transformer_one(self, intermedirair_data):
		final_categorized_data = {}
		for date, activity_info in intermedirair_data.iteritems():
			activity_id = self.above_threshold_exclusive_android_activity_decider(activity_info[self.intermediair_transformed_feature_activities],activity_info[self.intermediair_transformed_feature_confidences], 50)
			if activity_id != None:
				final_categorized_data[date] = {self.transformed_feature_attribute : activity_id}
				
		#sort by chronological order
		final_categorized_data = collections.OrderedDict(sorted(final_categorized_data.items()))
		
		return final_categorized_data
			
		
	def above_threshold_exclusive_android_activity_decider (self, activity_ids, confidences, threshold):
	
		if confidences[0] > threshold:
			return activity_ids[0]
			
		else:
			return None
	
	def count_sony_activity_realizations(self):
		activity_counts = {}
		original_sony_activity = self.nontransformed_data[self.sony_activity_feature]
		
		for date, activity_info in original_sony_activity.iteritems():
			activity = activity_info[self.sony_activity_motion]
			
			if activity not in activity_counts:
				activity_counts[activity] = 0 
				
				duration_millis = DataExtractor.end_date_of_realization_in_millis(date)-DataExtractor.start_date_of_realization_in_millis(date)
				activity_counts[activity] += duration_millis
		
		#transform the milliseconds to minutes
		for activity, duration_in_millis in activity_counts.iteritems():
			activity_counts[activity] = duration_in_millis/(1000.0*60)
		
		activity_counts = collections.OrderedDict(sorted(activity_counts.items(), key=lambda x: x[1], reverse = True))
		
		return activity_counts
		
	
	def count_android_activity_realizations(self):
		activity_counts = {}
		original_android_activity = self.nontransformed_data[self.android_activity_feature]
		
		for date, activity_info in original_android_activity.iteritems():
			activities = activity_info[self.android_activity_activities]
			#select the most probable non unknown activity
			for one_activity in activities:
				if one_activity not in self.android_unknown_activities:
					activity = one_activity
					break
			
			#check that the confidences array is well sorted->to ensure that the most probable activity were selected
			#confidences = self.transform_confidences_from_str_to_int_list(activity_info[self.android_activity_confidences])
			confidences = activity_info[self.android_activity_confidences]
			confidence = confidences[0]
			
			for one_confidence in confidences:
				if one_confidence > confidence:
					raise Exception ("BAD SORTING EXCEPTION: confidences badly sorted "+str(confidences))
				
				confidence = one_confidence
				
			if activity not in activity_counts:
				activity_counts[activity] = 0 
			
			duration_millis = DataExtractor.end_date_of_realization_in_millis(date)-DataExtractor.start_date_of_realization_in_millis(date)
			activity_counts[activity] += duration_millis
		
		#transform the milliseconds to minutes
		for activity, duration_in_millis in activity_counts.iteritems():
			activity_counts[activity] = duration_in_millis/(1000.0*60)
		
		activity_counts = collections.OrderedDict(sorted(activity_counts.items(), key=lambda x: x[1], reverse = True))
		
		return activity_counts
		
	def transform_confidences_from_str_to_int_list(self,confidences_str):
		confidences = []
		for conf_str in confidences_str.split(","):
			try:
				confidences.append(int(conf_str))
			except ValueError:
				print "empty value ignored in "+confidences_str
				return [0]
			
		return confidences	