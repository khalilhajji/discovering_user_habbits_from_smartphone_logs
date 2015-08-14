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
the applaunch transformer takes the initial applaunches and represent them as ids. 
The format of the data is:
	date : {id:id1} where the value of the attribute id is an integer representing the id of the app launch that occured at the specified date

The format of the metadata is;
	id: {id1: name1, id2 : name2 , ... , idn : namen}
'''
class ApplaunchTransformer (FeatureTransformer):
	transformed_feature_name = "appLaunch"
	transformed_feature_app_attribute="id"
	other_app_name = "other"
	
	app_feature = "appLaunch"
	app_name = "appName"
	
	
	def __init__(self, nontransformed_data):
		super(ApplaunchTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata[ApplaunchTransformer.transformed_feature_app_attribute]={}
		self.transformed_feature_data={}
		
		
		#add empty realizations if the app launch feature is not present in the data
		if self.app_feature not in self.nontransformed_data:
			self.nontransformed_data[self.app_feature] = {}
		
		#sort the app launches by increasing date
		print "ordering applaunches by date"
		self.nontransformed_data[self.app_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.app_feature].items()))	
		
		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		k=20
		#name_id = self.construct_metadata_for_all_app()
		name_id = self.construct_metadata_for_top_app(k)
		
		print "transforming data"
		#II- transform the data
		original_apps = self.nontransformed_data[self.app_feature]
		for date, app in original_apps.iteritems():
			if app[self.app_name] in name_id:
				id = name_id[app[self.app_name]]
			else:
				id = name_id[self.other_app_name]
			date = DataOperations.build_interval(date, date)
			if date in self.transformed_feature_data:
				raise Exception("Duplicate date app_launch Exception: two applications launched at "+date)
				
			self.transformed_feature_data[date]={self.transformed_feature_app_attribute : id}

		
	'''
	constructs the metadata taking into account all the app launches
	'''
	def construct_metadata_for_all_app(self):	
		#I- see all the different app launches and assign indicies to them
		#1- see all the different app names
		print "creating metadata"
		original_apps = self.nontransformed_data[self.app_feature]
		app_names = set()
		for date, app in original_apps.iteritems():
			app_names = set.union(app_names, set([app[self.app_name]]))
			
		
		#2-sort them by alphabetic order
		app_names = list(app_names)
		app_names.sort()
		
		#3-construct the metada information and a name_id dict. The ids of the apps are the alphabetic order their names
		name_id = {}
		id = 0
		for name in app_names:
			name_id[name]=id
			self.transformed_feature_metadata[ApplaunchTransformer.transformed_feature_app_attribute][id]=name
			id+=1
		
		return name_id
		
	
	'''
	construct metadata taking into account the top k apps launched and marking all the others in other apps launched
	'''
	def construct_metadata_for_top_app(self,k):
		#I- see all the different notifications and assign indicies to them
		#1- see all the different notification names
		print "creating metadata"
		original_apps = self.nontransformed_data[self.app_feature]
		app_counts = {}
		for date, app in original_apps.iteritems():
			appl_name = app[self.app_name]
			
			if appl_name not in app_counts:
				app_counts[appl_name] = 0
					
			app_counts[appl_name] += 1
			
		#2-select the k most frequent notifications
		app_counts = collections.OrderedDict(sorted(app_counts.items(), key=lambda k: k[1], reverse=True))
		app_names = app_counts.keys()[0:min(k,len(app_counts.keys()))]
		#3-sort them by alphabetic order
		app_names.sort()
		
		#3-construct the metada information and a name_id dict. The ids of the notifications are the alphabetic order their names
		name_id = {}
		id = 0
		for name in app_names:
			name_id[name]=id
			self.transformed_feature_metadata[ApplaunchTransformer.transformed_feature_app_attribute][id]=name
			id+=1
			
		name_id[self.other_app_name] = id
		self.transformed_feature_metadata[ApplaunchTransformer.transformed_feature_app_attribute][id]=self.other_app_name
			
		return name_id
		
		