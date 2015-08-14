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
the headset transformer transforms the battery data into indicies. 
The format of the data is:
	date : {plugged: id,
			microphone: id}
			
if there is no plug, then plugged -1. Same for microphone

if one of the attribute is unknown, it will not be present in the dictionary

The format of the metadata is;
	{plugged: {0: "Is plugged"},
	microphone:{1: "Is plugged"}
											}
											
'''
class HeadsetTransformer (FeatureTransformer):
	transformed_feature_name = "headset"
	transformed_feature_headset_plugged = "plugged"
	transformed_feature_headset_micro="microphone"
	
	#timeout is set to the equivalent of 15 minutes. if the same activity occurs in delta time smaller or equal to timeout, then we assume that, this activity was occuring in between
	timeout_in_millis = 1000*60*15
	
	headset_feature = "headsetPlug"
	headset_plug = "state"
	headset_micro = "microphone"
	
	
	
	def __init__(self, nontransformed_data):
		super(HeadsetTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata={}
		self.transformed_feature_data={}
		
		
		#add empty realizations if the notification feature is not present in the data
		if self.headset_feature not in self.nontransformed_data:
			self.nontransformed_data[self.headset_feature] = {}
		
		#sort the notifications by increasing date
		print "ordering headset info by date"
		self.nontransformed_data[self.headset_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.headset_feature].items()))	
		
		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		#I- construct metadata
		self.transformed_feature_metadata= {self.transformed_feature_headset_plugged: {0: "Is plugged"},
											self.transformed_feature_headset_micro:{1: "Is plugged"}
											}
		
				
		plugged_id_dict = {1 : 0,
						  0 : self.negation_value_constant,
						  }
						  
		micro_id_dict = {0 : self.negation_value_constant,
						  1 : 1}
						  
		counter_plug = {0:0, 1:0}
		counter_micro = {0:0, 1:0}
		
		
		#II- transform the data
		original_headset = self.nontransformed_data[self.headset_feature]
		print "transforming data"
		for date, headset_info in original_headset.iteritems():
			transformed_headset = {}
			if self.headset_plug in headset_info:
				transformed_headset[self.transformed_feature_headset_plugged]=plugged_id_dict[headset_info[self.headset_plug]]
			
			if self.headset_micro in headset_info:
				transformed_headset[self.transformed_feature_headset_micro]=micro_id_dict[headset_info[self.headset_micro]]
				
			if date in self.transformed_feature_data:
				raise Exception("Duplicate date battery Exception: two battery infos retreived at "+date)
			
			if transformed_headset.keys > 0:
				self.transformed_feature_data[date]=transformed_headset
			else:
				raise Exception("EMPTY VALUE EXCEPTION: the value constructed for headset is empty")	
		
		print "ordering the transformed headset data by date"
		self.transformed_feature_data = collections.OrderedDict(sorted(self.transformed_feature_data.items()))
		
		print "concatenating the close and same headset realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(self.transformed_feature_data)
		
		
		
		
		
		