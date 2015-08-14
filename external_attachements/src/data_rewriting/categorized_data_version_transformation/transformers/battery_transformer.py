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
the battery transformer transforms the battery data into indicies. 
The format of the data is:
	date : {health: id,
			plugged: id,
			type: id}
			
if there is no plug, then plugged and type takes the value -1

if one of the attribute is unknown, it will not be present in the dictionary

The format of the metadata is;
	{health: {0: "Good",
																					  1: "Cold",
																					  2: "Dead",
																					  3: "Overheat",
																					  },
											plugged:{4: "Is plugged"},
											type: {5: "AC charger",
																					6: "USB port",
																					7: "wireless plugging"
																					}
											}
'''
class BatteryTransformer (FeatureTransformer):
	transformed_feature_name = "battery"
	transformed_feature_battery_health="health"
	transformed_feature_battery_plugged = "plugged"
	transformed_feature_battery_type = "type"
	
	#timeout is set to the equivalent of 30 minutes. if the same activity occurs in delta time smaller or equal to timeout, then we assume that, this activity was occuring in between
	timeout_in_millis = 1000*60*30
	
	battery_feature = "battery_main"
	battery_health = "health"
	battery_plug = "plugged"
	
	forbidden_original_health_values = [0,1,5,6]
	
	
	def __init__(self, nontransformed_data):
		super(BatteryTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata={}
		self.transformed_feature_data={}
		
		
		#add empty realizations if the notification feature is not present in the data
		if self.battery_feature not in self.nontransformed_data:
			self.nontransformed_data[self.battery_feature] = {}
		
		#sort the notifications by increasing date
		print "ordering battery info by date"
		self.nontransformed_data[self.battery_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.battery_feature].items()))	
		
		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		#I- construct metadata
		self.transformed_feature_metadata= {self.transformed_feature_battery_health: {0: "Good",
																					  1: "Cold",
																					  2: "Dead",
																					  3: "Overheat",
																					  },
											self.transformed_feature_battery_plugged:{4: "Is plugged"},
											self.transformed_feature_battery_type: {5: "AC charger",
																					6: "USB port",
																					7: "wireless plugging"
																					}
											}
		
				
		health_id_dict = {2 : 0,
						  7 : 1,
						  4 : 2,
						  3 : 3,
						  }
						  
		plugged_id_dict = {0 : self.negation_value_constant,
						  1 : 4,
						  2 : 4,
						  4 : 4}
						  
		type_id_dict = {0 : self.negation_value_constant,
						  1 : 5,
						  2 : 6,
						  4 : 7}
		
		
		#II- transform the data
		original_battery = self.nontransformed_data[self.battery_feature]
		print "transforming data"
		for date, battery_info in original_battery.iteritems():
			transformed_battery = {}
			if self.battery_health in battery_info and battery_info[self.battery_health] not in self.forbidden_original_health_values:
				transformed_battery[self.transformed_feature_battery_health]=health_id_dict[battery_info[self.battery_health]]
			
			if self.battery_plug in battery_info:
				transformed_battery[self.transformed_feature_battery_plugged]=plugged_id_dict[battery_info[self.battery_plug]]
				transformed_battery[self.transformed_feature_battery_type]=type_id_dict[battery_info[self.battery_plug]]
				
			if date in self.transformed_feature_data:
				raise Exception("Duplicate date battery Exception: two battery infos retreived at "+date)
			
			if transformed_battery.keys > 0:
				self.transformed_feature_data[date]=transformed_battery
			else:
				raise Exception("EMPTY VALUE EXCEPTION: the value constructed for battery is empty")
				
				
		print "ordering the transformed battery data by date"
		self.transformed_feature_data = collections.OrderedDict(sorted(self.transformed_feature_data.items()))
		
		print "concatenating the close and same battery realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(self.transformed_feature_data)
		
		
		
		