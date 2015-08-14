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


'''
the notification transformer takes the initial notifications and represent them as ids. 
The format of the data is:
	date : {id:[id1,id2]} where the value of the attribute id is an array representing the ids of the notifications that occured at the specified date

The format of the metadata is;
	id: {id1: name1, id2 : name2 , ... , idn : namen}
'''
class NotificationTransformer (FeatureTransformer):
	transformed_feature_name = "notification"
	transformed_feature_notif_attribute="id"
	other_notif_name = "other"
	
	notif_feature = "notification"
	notif_name = "packageName"
	notif_date_millis = "postTimeTimeZone"
	notif_date_readable = "rpostTimeTimeZone"
	
	
	app_feature = "appLaunch"
	app_name = "appName"
	
	
	def __init__(self, nontransformed_data):
		super(NotificationTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata[NotificationTransformer.transformed_feature_notif_attribute]={}
		self.transformed_feature_data={}
		
		
		#add empty realizations if the notification feature is not present in the data
		if self.notif_feature not in self.nontransformed_data:
			self.nontransformed_data[self.notif_feature] = {}
			
		if self.app_feature not in self.nontransformed_data:
			self.nontransformed_data[self.app_feature] = {}
		
		#sort the notifications by increasing date
		print "ordering notifications by date"
		self.nontransformed_data[self.notif_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.notif_feature].items()))	
		
		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		k = 20
		notifcations_allowed = self.list_notifications_corresponding_to_app()
		#name_id = self.construct_metadata_for_all_notif(notifcations_allowed)
		name_id = self.construct_metadata_for_top_notif(k, notifcations_allowed)
		
		print "transforming data"
		#II- transform the data
		original_notifs = self.nontransformed_data[self.notif_feature]
		for common_date, notif_array in original_notifs.iteritems():
			for notif in notif_array:
				if notif[self.notif_name] in name_id:
					id = name_id[notif[self.notif_name]]
				elif notif[self.notif_name] in notifcations_allowed:
					id = name_id[self.other_notif_name]
				else:
					id = None
				date = DataOperations.instanciate_interval(notif[self.notif_date_readable], notif[self.notif_date_millis])
				if date not in self.transformed_feature_data:
					self.transformed_feature_data[date]={self.transformed_feature_notif_attribute : []}
				
				if id != None and id not in self.transformed_feature_data[date][self.transformed_feature_notif_attribute]:
					self.transformed_feature_data[date][self.transformed_feature_notif_attribute].append(id)

		
	'''
	constructs the metadata taking into account all the notifications
	'''
	def construct_metadata_for_all_notif(self):	
		#I- see all the different notifications and assign indicies to them
		#1- see all the different notification names
		print "creating metadata"
		original_notifs = self.nontransformed_data[self.notif_feature]
		notif_names = set()
		for common_date, notif_array in original_notifs.iteritems():
			current_notif_names = {notif[self.notif_name] for notif in notif_array}
			notif_names = set.union(notif_names, current_notif_names)
			
		
		#2-sort them by alphabetic order
		notif_names = list(notif_names)
		notif_names.sort()
		
		#3-construct the metada information and a name_id dict. The ids of the notifications are the alphabetic order their names
		name_id = {}
		id = 0
		for name in notif_names:
			name_id[name]=id
			self.transformed_feature_metadata[NotificationTransformer.transformed_feature_notif_attribute][id]=name
			id+=1
			
		return name_id
		
	
	def list_notifications_corresponding_to_app(self):
		original_apps = self.nontransformed_data[self.app_feature]
		app_names = set()
		for date, app in original_apps.iteritems():
			app_names = set.union(app_names, set([app[self.app_name]]))
			
		
		#2-sort them by alphabetic order
		app_names = list(app_names)
		app_names.sort()
		return app_names
		
	
	'''
	construct metadata taking into account the top k notifications and marking all the others in other notifications
	'''
	def construct_metadata_for_top_notif(self,k, notifcations_allowed):
		#I- see all the different notifications and assign indicies to them
		#1- see all the different notification names
		print "creating metadata"
		original_notifs = self.nontransformed_data[self.notif_feature]
		notif_counts = {}
		for common_date, notif_array in original_notifs.iteritems():
			current_notif_names = {notif[self.notif_name] for notif in notif_array if notif[self.notif_name] in notifcations_allowed}
			for notif_name in current_notif_names:
				if notif_name not in notif_counts:
					notif_counts[notif_name] = 0
					
				notif_counts[notif_name] += 1
			
		#2-select the k most frequent notifications
		notif_counts = collections.OrderedDict(sorted(notif_counts.items(), key=lambda k: k[1], reverse=True))
		notif_names = notif_counts.keys()[0:min(k,len(notif_counts.keys()))]
		#3-sort them by alphabetic order
		notif_names.sort()
		
		#3-construct the metada information and a name_id dict. The ids of the notifications are the alphabetic order their names
		name_id = {}
		id = 0
		for name in notif_names:
			name_id[name]=id
			self.transformed_feature_metadata[NotificationTransformer.transformed_feature_notif_attribute][id]=name
			id+=1
			
		name_id[self.other_notif_name] = id
		self.transformed_feature_metadata[NotificationTransformer.transformed_feature_notif_attribute][id]=self.other_notif_name
			
		return name_id
		
		