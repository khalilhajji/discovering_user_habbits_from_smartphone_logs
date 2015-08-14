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
from abc import *


'''
the bluetooth transformer takes the initial paring devices and represent them as ids.

The output is two features:

I)	bluetoothPaired feature that represents the devices that are paired with the smartphone.

The format of the data is:
	date : {device: [id1, id2]} where the value of the attribute device is an id that represents the device paired or being paired to at the specified date

The format of the metadata is;
	device: {id1: {name: name1,
				   address: adress1}, 
			id2 : {name: name2,
				   address: address2},
			... , 
			idn : {name:namen,
				   address: addressn}
			}
			
II) bluetoothSeen feature that represents the devices seen by the smartphone

The format of the data is:
	date : {device: [id1, id2]} where the value of the attribute device is an id that represents the device seen to at the specified date

	there is a boolean is_exclusive, that indicates if the seen ids take into account the paired devices or only the seen and not paired devices
	
the metadat has the same format than I)


'''
class BluetoothTransformer(FeatureTransformer):
	__metaclass__ = ABCMeta
	#timeout is set to the equivalent of 30 minutes. if the same activity occurs in delta time smaller or equal to timeout, then we assume that, this activity was occuring in between
	timeout_in_millis = 1000*60*30
	
	transformed_feature_metabluetooth_name = "name"
	transformed_feature_metabluetooth_mac = "address"
	transformed_feature_bluetooth_attribute="device"
	other_mac_name = "other"
	other_device_name = "other"
	
	bluetooth_feature = "bluetooth"
	bluetooth_name = "name"
	bluetooth_mac = "address"
	bluetooth_state = "bondState"
	
	k = 20
	
	
	bluetooth_paired_value = [12 ,  "BOND_BONDED", 11, "BOND_BONDING"]
	bluetooth_not_paired_value = [10, "BOND_NONE"]
	
	def __init__(self, nontransformed_data):
		super(BluetoothTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata={}
		self.transformed_feature_data={}
		
		
		#add empty realizations if the bluetooth feature is not present in the data
		if self.bluetooth_feature not in self.nontransformed_data:
			self.nontransformed_data[self.bluetooth_feature] = {}
		
		#sort the notifications by increasing date
		print "ordering bluetooth by date"
		self.nontransformed_data[self.bluetooth_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.bluetooth_feature].items()))	
	
	@abstractmethod
	def transform(self):
		return None
		
	def construct_metadata_for_all_devices(self):
		#I- see all the different bleutooth devices and assign indicies to them
		#1- see all the different bluetooth names
		print "creating metadata"
		original_bluetooth = self.nontransformed_data[self.bluetooth_feature]
		bluetooth_mac = set()
		mac_names_dict = {}
		for common_date, bluetooth_array in original_bluetooth.iteritems():
			for device in bluetooth_array:
				name = device[BluetoothTransformer.bluetooth_name]
				mac = device[BluetoothTransformer.bluetooth_mac]
					
				if mac not in mac_names_dict:
					mac_names_dict[mac]= []
					
				if name not in mac_names_dict[mac]:
					mac_names_dict[mac].append(name)
				
				
					
				bluetooth_mac = set.union(bluetooth_mac, set([mac]))
				
		#2-sort them by alphabetic order
		bluetooth_mac = list(bluetooth_mac)
		bluetooth_mac.sort()
			
		#3-construct the metada information and a name_id dict. The ids of the bluetooth are the alphabetic order of their names
		mac_id = {}
		id = 0
		self.transformed_feature_metadata[BluetoothTransformer.transformed_feature_bluetooth_attribute]= {}
		for mac in bluetooth_mac:
			mac_id[mac]=id
			self.transformed_feature_metadata[BluetoothTransformer.transformed_feature_bluetooth_attribute][id]= {BluetoothTransformer.transformed_feature_metabluetooth_name : mac_names_dict[mac],
																														BluetoothTransformer.transformed_feature_metabluetooth_mac : mac}											
			id+=1
		
		return mac_id
		
		
	'''
	construct metadat taking into account :
		- the most frequent 20 seen devices
	'''
	def construct_metadata_for_top_k_devices(self, k):
		#I- see all the different bleutooth devices and assign indicies to them
		#1- see all the different bluetooth names
		print "creating metadata"
		original_bluetooth = self.nontransformed_data[self.bluetooth_feature]
		bluetooth_mac_counts = {}
		mac_names_dict = {}
		for common_date, bluetooth_array in original_bluetooth.iteritems():
			for device in bluetooth_array:
				name = device[BluetoothTransformer.bluetooth_name]
				mac = device[BluetoothTransformer.bluetooth_mac]
					
				if mac not in mac_names_dict:
					mac_names_dict[mac]= []
					
				if name not in mac_names_dict[mac]:
					mac_names_dict[mac].append(name)
				
				
				if mac not in bluetooth_mac_counts:
					bluetooth_mac_counts[mac] = 0
					
				bluetooth_mac_counts[mac] +=1
		
		#2-select the k most frequent notifications
		bluetooth_mac_counts = collections.OrderedDict(sorted(bluetooth_mac_counts.items(), key=lambda k: k[1], reverse=True))
		bleutooth_macs = bluetooth_mac_counts.keys()[0:min(k,len(bluetooth_mac_counts.keys()))]
		
		#3-sort them by alphabetic order
		bleutooth_macs.sort()		
		
			
		#4-construct the metada information and a name_id dict. The ids of the bluetooth are the alphabetic order of their names
		mac_id = {}
		id = 0
		self.transformed_feature_metadata[BluetoothTransformer.transformed_feature_bluetooth_attribute]= {}
		for mac in bleutooth_macs:
			mac_id[mac]=id
			self.transformed_feature_metadata[BluetoothTransformer.transformed_feature_bluetooth_attribute][id]= {BluetoothTransformer.transformed_feature_metabluetooth_name : mac_names_dict[mac],
																														BluetoothTransformer.transformed_feature_metabluetooth_mac : mac}
														
			id+=1
		
		mac_id[self.other_mac_name]=id
		self.transformed_feature_metadata[BluetoothTransformer.transformed_feature_bluetooth_attribute][id]= {BluetoothTransformer.transformed_feature_metabluetooth_name : [self.other_device_name],
																														BluetoothTransformer.transformed_feature_metabluetooth_mac : self.other_mac_name}
	
		return mac_id
	
	


class BluetoothPairedTransformer (BluetoothTransformer):
	transformed_feature_name = "bluetoothPaired"
	
	def __init__(self, nontransformed_data):
		super(BluetoothPairedTransformer, self).__init__(nontransformed_data)
		
		
		
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		#mac_id = self.construct_metadata_for_all_devices()
		mac_id = self.construct_metadata_for_top_k_devices(self.k)
		
		print "transforming data"
		#II- transform the data
		original_bluetooth = self.nontransformed_data[self.bluetooth_feature]
		for common_date, bluetooth_array in original_bluetooth.iteritems():
			for device in bluetooth_array:
				if device[BluetoothPairedTransformer.bluetooth_state] not in BluetoothPairedTransformer.bluetooth_paired_value and device[BluetoothPairedTransformer.bluetooth_state] not in BluetoothPairedTransformer.bluetooth_not_paired_value:
					raise Exception("UNKNOWN VALUE EXCEPTION: the bondstate value of the device is unknown")
				
				if device[BluetoothPairedTransformer.bluetooth_state] in BluetoothPairedTransformer.bluetooth_paired_value:
					if device[BluetoothPairedTransformer.bluetooth_mac] in mac_id:
						id = mac_id[device[BluetoothPairedTransformer.bluetooth_mac]]
					else :
						id = mac_id[self.other_mac_name]
					date = common_date
					if date not in self.transformed_feature_data:
						self.transformed_feature_data[date]={self.transformed_feature_bluetooth_attribute : []}
					
					if id not in self.transformed_feature_data[date][self.transformed_feature_bluetooth_attribute]:
						self.transformed_feature_data[date][self.transformed_feature_bluetooth_attribute].append(id)
						
		print "ordering the transformed bluetooth paired data by date"
		self.transformed_feature_data = collections.OrderedDict(sorted(self.transformed_feature_data.items()))
		
		print "concatenating the close and same bluetooth paired realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(self.transformed_feature_data)

					

					
class BluetoothSeenTransformer (BluetoothTransformer):
	
	transformed_feature_name = "bluetoothSeen"
	
	
	#when true, the seen features contains only the seen and not paired devices
	is_exclusive = True
	def __init__(self, nontransformed_data):
		super(BluetoothSeenTransformer, self).__init__(nontransformed_data)
		
		
		
	
	def transform(self):
		#mac_id = self.construct_metadata_for_all_devices()
		mac_id = self.construct_metadata_for_top_k_devices(self.k)
		print "transforming data"
		#II- transform the data
		original_bluetooth = self.nontransformed_data[self.bluetooth_feature]
		for common_date, bluetooth_array in original_bluetooth.iteritems():
			for device in bluetooth_array:
				if device[BluetoothPairedTransformer.bluetooth_state] not in BluetoothPairedTransformer.bluetooth_paired_value and device[BluetoothPairedTransformer.bluetooth_state] not in BluetoothPairedTransformer.bluetooth_not_paired_value:
					raise Exception("UNKNOWN VALUE EXCEPTION: the bondstate value of the device is unknown")
				

				if (not self.is_exclusive) or (self.is_exclusive and device[BluetoothPairedTransformer.bluetooth_state] in BluetoothPairedTransformer.bluetooth_not_paired_value):
					if device[BluetoothPairedTransformer.bluetooth_mac] in mac_id:
						id = mac_id[device[BluetoothPairedTransformer.bluetooth_mac]]
					else :
						id = mac_id[self.other_mac_name]
					date = common_date
					if date not in self.transformed_feature_data:
						self.transformed_feature_data[date]={self.transformed_feature_bluetooth_attribute : []}
					
					if id not in self.transformed_feature_data[date][self.transformed_feature_bluetooth_attribute]:
						self.transformed_feature_data[date][self.transformed_feature_bluetooth_attribute].append(id)
		
		print "ordering the transformed bluetooth seen data by date"		
		self.transformed_feature_data = collections.OrderedDict(sorted(self.transformed_feature_data.items()))
		
		print "concatenating the close and same bluetooth seen realizations"
		self.transformed_feature_data = self.concatenate_successive_realizations(self.transformed_feature_data)
		
		
		