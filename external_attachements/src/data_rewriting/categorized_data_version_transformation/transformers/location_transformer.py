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
the location transformer takes the initial dataset and extract the location of the user. The goal is to extract a location that meanful to the user.
It means that two very close Gps coordinates should be considered as the same location.

for that purpose, to extract this location, the Wifi names seen by the user, his gps coordinates and the gps coordinates of the base station connected to the phone
are combined to extract that location.

The idea is the following: all the Wi-fi names seens simultaneously by the user represents the same place. Then we try to map the Gps coordinates into those Wi-Fi groups.

NOTE: The code written here can be more optimized in the sence of the running time. However, as the extraction of the place is a complex operation, we previliged the clarity and the understability of the code rather
than it`s performance.
'''
class LocationTransformer (FeatureTransformer):
	transformed_feature_name = "location"
	transformed_feature_location_attribute="place"
	other_location_id = -1
	
	location_feature = "location"
	location_lat = "latitude"
	location_long = "longitude"
	location_acc = "accuracy"
	
	wifi_feature = "wifiAps"
	wifi_name = "ssid"
	
	wifi_connected_feature = "wifiConnectedAp"
	wifi_name= "ssid"
	
	station_feature = "telephony"
	station_lat="cdmaCellLocBaseStationLat"
	station_long = "cdmaCellLocBaseStationLng"
	
	#the maximum distance in meters that two points in the same location could have
	max_cluster_distance_threshold = 1500
	
	#if two wifi groups have at least a threshold number of common wifis, then we consider that those wifis form the same cluster
	wifi_intersection_threshold = 3 
	
	#the maximum amount of time allowed to consider two realizations as adjacent ones. NB: 3600000 milliseconds corresponds to 1 hour
	timeout_millis=long(1800000)
	
	#we suppose that a wifi cannot be seen starting from a distance max_wifi_range_in_meters 
	max_wifi_range_in_meters = 300
	
	#we suppose that if a wifi is assigned to the same cluster during at least 10 different days, then it is not a mobile wifi
	min_days_of_observed_wifi = 13
	
	#the locations that have a minimum accuracy bigger than 200 meters should be removed
	min_accuracy_threshold = 200
	
	
	
	
	
	def __init__(self, nontransformed_data):
		super(LocationTransformer, self).__init__(nontransformed_data)
		self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]={}
		self.transformed_feature_data={}
		
		self.wifi_locid = {}
		self.gps_locid = {}
		self.station_locid={}
		
		#some wifis are mobile wifis and are not representative of the location, thus this list contains the wifis that we have the certitude that they are stable and thus representative of the location
		self.stable_wifis=None
		
		self.location_id=0
		
		#add empty realizations for the features that are not present in the data
		if self.wifi_feature not in self.nontransformed_data:
			self.nontransformed_data[self.wifi_feature] = {}
		
		if self.location_feature not in self.nontransformed_data:
			self.nontransformed_data[self.location_feature] = {}
			
		if self.station_feature not in self.nontransformed_data:
			self.nontransformed_data[self.station_feature] = {}
			
		#sort the corresponding entries by increasing date
		print "ordering wifi, location and station by date"
		self.nontransformed_data[self.wifi_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.wifi_feature].items()))
		self.nontransformed_data[self.location_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.location_feature].items()))
		self.nontransformed_data[self.station_feature] = collections.OrderedDict(sorted(self.nontransformed_data[self.station_feature].items()))
		
		#filter the original location feature by removing all the entries that have a minimal accuracy bigger than threshold
		print "filtering gps locations by accuracy"
		self.filter_locations()
		

		
	'''
	filter the original location feature by removing all the entries that have a minimal accuracy bigger than threshold
	'''
	def filter_locations(self):
		for date in self.nontransformed_data[self.location_feature].keys():
			min_original_location_accuracy = min(self.nontransformed_data[self.location_feature][date][self.location_acc])
			if min_original_location_accuracy>LocationTransformer.min_accuracy_threshold:
				del self.nontransformed_data[self.location_feature][date]
			
	
	'''
	consider data and metadata with only the top most visited k locations. The others will be in others
	'''
	def consider_only_top_k_locations(self, k):
		print "isolating the top "+str(k)+" locations"
		transformed_data = self.transformed_feature_data
		locations_count = {}
		
		for data, location in transformed_data.iteritems():
			locid = location[self.transformed_feature_location_attribute]
			if locid not in locations_count:
				locations_count[locid] = 0
			
			locations_count[locid] +=1
			
		
		#2-select the k most frequent notifications
		locations_count = collections.OrderedDict(sorted(locations_count.items(), key=lambda k: k[1], reverse=True))
		location_ids = locations_count.keys()[0:min(k,len(locations_count.keys()))]
		
		#construct the metadata, the most frequent location will have the id 0, the second most frequent the id 1, ect
		new_metadata = {self.transformed_feature_location_attribute : {}}
		
		newid = 0
		place_id = {}
		for locationid in location_ids:
			place_id[locationid]=newid
			new_metadata[LocationTransformer.transformed_feature_location_attribute][newid] = self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][locationid]
			
			newid+=1
		
		place_id[self.other_location_id]=newid
		new_metadata[LocationTransformer.transformed_feature_location_attribute][newid] = {"wifi":["other"], "gps":["other"], "station": ["other"]}
		
		self.transformed_feature_metadata = new_metadata
		
		#transform the locations in the data
		new_data = {}
		
		for date, location in transformed_data.iteritems():
			old_locid = location[self.transformed_feature_location_attribute]
			
			if old_locid in place_id:
				new_locid = place_id[old_locid]
			else:
				new_locid = place_id[LocationTransformer.other_location_id]
			
			new_data[date] = {LocationTransformer.transformed_feature_location_attribute:new_locid}
			
			
		new_data = collections.OrderedDict(sorted(new_data.items()))
		self.transformed_feature_data = new_data
			
			
		
		
	
	'''
	does the extraction and the transformation of the location starting from the cleaned version of the dataset
	'''
	def transform(self):
		#k is used at the last line of method transform
		k = 20
		#create location cluster such that, for each wifi, location, or station get the id of the corresponding location (read comments and code of cluster_locations for more information)
		#those are the initial clusters, however they will be opitmized and might change in the following steps
		self.cluster_locations()
		
		print "checking max distance"
		self.location_max_distance_check()
		print "checking max distance : succeeded"
		
		
		DateTimeUtils.start_chrono()
		#transform the initial gps locations, the initial wifis and the initial gsm base stations to location ids and make merges when possible
		original_data = self.nontransformed_data
		original_locations = original_data[self.location_feature]
		
		first_transformed_data = {}
		last_location = None
		last_date = None
		for date, gps in original_locations.iteritems():
			gps_coordinates = GpsUtils.to_string(gps[self.location_lat], gps[self.location_long])
			location = self.gps_locid[gps_coordinates]
			
			
			date = self.update_location_data(first_transformed_data, last_date, last_location, date, location)
			last_location = location
			last_date = date
	
		
		original_wifis = original_data[self.wifi_feature]
		last_location = None
		last_date = None
		for date, wifis in original_wifis.iteritems():
			#take one of the seen wifis (they are all mapped to the same location id)
			wifi_names = {wifi[self.wifi_name] for wifi in wifis if wifi[self.wifi_name] in self.stable_wifis}
			if len(wifi_names)>0:
				one_wifi_name = next(iter(wifi_names))
				location = self.wifi_locid[one_wifi_name]
				date = self.update_location_data(first_transformed_data, last_date, last_location, date, location)
				last_location = location
				last_date = date

		
		
		original_stations = original_data[self.station_feature]
		last_location = None
		last_date = None
		for date, station in original_stations.iteritems():
			station_coordinates = GpsUtils.to_string(station[self.station_lat], station[self.station_long])
			location = self.station_locid[station_coordinates]
			date = self.update_location_data(first_transformed_data, last_date, last_location, date, location)
			last_location = location
			last_date = date
		
		#as we mapped all the entries to loc_ids, we no longer need the wifi_locid, gps_locid and the station_locid dicts. for safety reasons we put them to None
		self.wifi_locid = None
		self.gps_locid = None
		self.station_locid=None

			
		duration = DateTimeUtils.stop_chrono()
		print "first replacement by location ids took "+str(duration)
		#now that we have mapped all the concerned features into location ids, we need to sort them by increasing chronological order and then start to collapse the intersecting time intervals
		#1- sort
		first_transformed_data = collections.OrderedDict(sorted(first_transformed_data.items()))
		
		'''
		2-merging clusters:
		2.1- time overlapping merge : in this stage we may encounter two realization that overlaps and that have different location ids.
		This is because we extended in the previous step the times for each location when it was possible and we could
		have not catched some realizations that co-occured in the same time before that extention. Thus we could have mapped 
		two cooccurent realizations in different clusters. In this stage, if we meet two overlapping locations that are different,
		it means that we missed to put them in the same cluster and we will collapse those two clusters in one cluster.
		'''
		DateTimeUtils.start_chrono()
		previous_location = None
		previous_date = None
		
		'''
		The role of the cluster_id_mapper is very important:
		When a cluster i is mapped to a cluster j, we store it in the cluster_id_mapper so that we can map all the realizations of the cluster i to the cluster j
		'''
		cluster_id_mapper = {}
		for date, location in first_transformed_data.iteritems():
			if (previous_location != None) and (DataOperations.does_date_overlaps(previous_date, date)) and (location != previous_location):
				#need to merge the two clusters and put the id of the right cluster in the two entries
				#there is only one exception where we do not merge two overlapping locations, this is when the following two conditions hold:
				#1- the locations are too far (i.e max_distance>max_cluster_distance_threshold)
				#2- the location 1 ended at the same time when the location 2 started
				#we do this because the recorder has some noise in recording the times that could explain that two different locations are adjacent in the time
				print "merge cluster "+str(location[self.transformed_feature_location_attribute])+" into "+str(previous_location[self.transformed_feature_location_attribute])
				
				if DataOperations.is_ended_at_the_start_of(previous_date , date):
					#it two location just overlap in the border (the end time of one is the beginning time of the other, we check that they are reasonably far before merging them in the same cluster.
					#Indeed it may happen that two locations that do not represent the same cluster (i,e they ae very far) appear the one just after the other (recorder time noise)
					merged_cluster_id = self.merge_clusters(cluster_id_mapper, previous_location[self.transformed_feature_location_attribute], location[self.transformed_feature_location_attribute], True)
					if merged_cluster_id == -1:
						print "WARNING: The two locations "+str(previous_location[self.transformed_feature_location_attribute])+" and "+str(location[self.transformed_feature_location_attribute])+" appeared at "+previous_date+" and "+date+" but do not represent the same location"

				else:
					#if two locations overlaps, then we merge them no matter how much they are far => they represent certainly the same cluster
					merged_cluster_id = self.merge_clusters(cluster_id_mapper, previous_location[self.transformed_feature_location_attribute], location[self.transformed_feature_location_attribute], False)
					
				if merged_cluster_id != -1:
					#merge succesful
					location[self.transformed_feature_location_attribute]= merged_cluster_id
					previous_location[self.transformed_feature_location_attribute] = merged_cluster_id
				
			if (previous_location == None) or DataOperations.is_ended_before(previous_date, date):	
				previous_location = location
				previous_date = date
		
		duration = DateTimeUtils.stop_chrono()
		print "first cluster merging took "+str(duration)
		
		'''
		2.2 space overlapping merge : There is another merge case that we want to cover: 
			It may happen that 2 clusters were not clustered together whereas they represent the same locations (we never saw two groups co-occuring in the time).
			Thus, in the second clustering stage we do the following:
			1- First we change the representation of our clusters with making the following assumption:
				a cluster regroups all the point in a cercle that has a center the center of the cluster and that has a radius equal to the maximum distance that 
				separates a point in the cluster from the center
			
			2- Second if two clusters overlaps in the space, then we merge them.
				cluster1 and cluster2 overlaps => r1+r2>= distance(center1, center2)
		'''
		DateTimeUtils.start_chrono()
		
		converged = False
		
		pass_num = 0
		while not converged:
			pass_num +=1
			print "Second merge : pass number "+str(pass_num)
		
			iter_num = 0
			is_change = False
			nb_clusters = len(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys())
			
			#sort them by size where size is the number of gps points contained in the cluster. The biggest cluster appears at the first position
			self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute] = collections.OrderedDict(sorted(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].items(), key=lambda k: (len(k[1]["gps"])+len(k[1]["station"])), reverse=True))
			i=0 
			while i<(nb_clusters-1):
				iter_num +=1
				print "Second merge progress : iteration "+str(iter_num)+" / "+str((len(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys())))
				
				
				first_cluster_id = self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys()[i]
				
				all_gps_coordinates = list(set.union(set(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["gps"]),set(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["station"])))
				if len(all_gps_coordinates)<=1:
					#as 2 clusters of one gps coordinate (radius=0) cannot overlap, for performance reasons we eliminate all the cases were we test for their overlapping by looping only over the
					#ones that have at least 2 coordinates in the outer loop
					#the first cluster with only one gps coordinates indicates that all the next ones will also be with one gps coordinate, so we stop the loop
					break
					

				#add the baricenter and the radius entry if we do not have them to the cluster
				if "center" not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]:
					[max_distance, second_max_distance, extreme_point, second_extreme_point, baricenter] = GpsUtils.max_distance_to_baricenter(all_gps_coordinates,0)
					self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["center"] = baricenter
					self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["radius"] = max_distance
				for j in range((len(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys())-1), i, -1):
					second_cluster_id = self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys()[j]
					if second_cluster_id in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
						#this cluster still exsists, was not merged before	
						#add the baricenter and the radius entry if we do not have them
						if "center" not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]:
							all_gps_coordinates = list(set.union(set(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["gps"]),set(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["station"])))
							[max_distance, second_max_distance, extreme_point, second_extreme_point, baricenter] = GpsUtils.max_distance_to_baricenter(all_gps_coordinates,0)
							self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["center"] = baricenter
							self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["radius"] = max_distance
								
						#see if the two clusters overlaps in the space => the intersection between the two circles is not empty
						if first_cluster_id != second_cluster_id:
							#cluster1 and cluster2 overlaps => r1+r2>= distance(center1, center2)
							dist_baricenters = GpsUtils.distance_from_str(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["center"] , self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["center"])
							does_overlaps = (self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["radius"]+self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["radius"]>=dist_baricenters)
							if does_overlaps:
								print "merge cluster "+str(second_cluster_id)+" with radius "+str(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][second_cluster_id]["radius"])+" and cluster "+str(first_cluster_id)+" with radius "+str(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][first_cluster_id]["radius"])+" : baricenter distance -> "+str(dist_baricenters)
								self.merge_clusters(cluster_id_mapper, first_cluster_id, second_cluster_id, False)
								is_change = True
				i+=1	
				nb_clusters = len(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys())
							
			if not is_change:
				converged = True
						
		
		duration = DateTimeUtils.stop_chrono()
		print "second cluster merging took "+str(duration)			
		#if we have jumps in the number of cluster ids we right shif the cluster ids to fill the jums.
		#We want that all cluster ids are successive with no gaps
		self.make_cluster_numbers_successive(cluster_id_mapper)
		
		#3-replace all the locations by their new mapped cluster ids and merge the locations if possible
		DateTimeUtils.start_chrono()
		previous_location_id = None
		previous_date = None
		collapsed_transformed_feature_data= {}
		for current_date, current_location in first_transformed_data.iteritems():
			#replace the current_location cluster id by the new computed one
			current_location_id = self.find_mapped_cluster_id(cluster_id_mapper, current_location[self.transformed_feature_location_attribute])
			current_location[self.transformed_feature_location_attribute]=current_location_id
			
			#safety check: At this stage two overlapping locations must have the same id
			if (previous_location_id != None) and (DataOperations.does_date_overlaps(previous_date, current_date) and not DataOperations.is_ended_at_the_start_of(previous_date , current_date) ) and (current_location_id != previous_location_id):
				raise Exception(("Non coherent location value: the times "+previous_date+" and "+current_date+" are overlapping and the respective corresponding locations "+
						str(previous_location_id)+" and "+str(current_location_id)+" are not the same"))
			
			#update the dataset
			current_date = self.update_location_data(collapsed_transformed_feature_data, previous_date, previous_location_id, current_date, current_location_id)
			
			previous_location_id = current_location_id
			previous_date = current_date
		
		
		duration = DateTimeUtils.stop_chrono()
		print "final location id replacement took "+str(duration)		
		collapsed_transformed_feature_data = collections.OrderedDict(sorted(collapsed_transformed_feature_data.items()))
		self.transformed_feature_data = collapsed_transformed_feature_data
		
		#here we transform again the data and metadata so that we consider only the top k locations
		self.consider_only_top_k_locations(k)
		
		

	'''
	verifies that each gps is mapped to exactly one location_id
	verifies that each station is mapped to exactly one location_id
	raise an exception if an error occurs, otherwise transforms values of the dicts from set(1) to one element
	'''
	def location_unicity_check(self):
		#check that each gps coordinate is mapped to exactly one location_id
		for gps, loc_ids in self.gps_locid.iteritems():
			if len(loc_ids)!=1:
				raise Exception("the gps coordinate "+gps+" has "+str(len(loc_ids))+" location ids : "+str(loc_ids))
			else:
				self.gps_locid[gps]=next(iter(loc_ids))
				
		#check that each station coordinate is mapped to exactly one location_id
		for station, loc_ids in self.station_locid.iteritems():
			if len(loc_ids)!=1:
				raise Exception("the base station "+station+" has "+str(len(loc_ids))+" location ids : "+str(loc_ids))
			else:
				self.station_locid[station] = next(iter(loc_ids))
				
	'''
	verfies that all the wifis that appear together have the same location id
	'''
	def location_wifi_coherence_check(self):
		#check that all wifis that appears together have the same location id
		original_wifis = self.nontransformed_data[self.wifi_feature]
		for date, wifis in original_wifis.iteritems():
			wifi_names = {wifi[self.wifi_name] for wifi in wifis if wifi[self.wifi_name] in self.stable_wifis}
			
			if len(wifi_names)>0:
				#take one of the seen wifis (they are all mapped to the same location id)
				one_wifi_name = next(iter(wifi_names))
				location = self.wifi_locid[one_wifi_name]
				
				for wifi in wifi_names:
					current_location = self.wifi_locid[wifi]
					if current_location != location:
						raise Exception("the wifis "+JsonUtils.dict_as_json_str(list(wifi_names))+" are assigned to different locations")
		
				
	'''
	check that the maximum distance that separates two points in the same location do not exceed the maximum distance threshold.
	Raise an exception if it is the case.
	'''
	def location_max_distance_check(self):
		for loc_id, dict in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].iteritems():
			# take the union of the gps points and the station points that both are represented as lat,long coordinates
			coordinates = set.union(set(dict["gps"]), set(dict["station"]))
			
			#check if the maximum distance that separates two points exceeds the allowed threshold
			if not GpsUtils.is_max_distance_less_or_equal_than(coordinates, self.max_cluster_distance_threshold):
				[max_distance,extreme_point_1,extreme_point_2,baricenter] = GpsUtils.max_distance(coordinates, self.max_cluster_distance_threshold)
				raise Exception( ("Threshold distance violated : the points "+extreme_point_1+" and "+extreme_point_2+" both belong to the location "+str(loc_id)+" and are separated by a distance of "+str(max_distance)+"\n"+
						"location "+str(loc_id)+" display : \n"+JsonUtils.dict_as_json_str(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id])))
					
						
		
	'''
	Regroup the wifi, the gps coordinate and the base station coordinates in clusters that represents locations.
	The idea is the following:
	At a time t, The wifi seen by the smartphone, the gps places visited by the user and the station to which the phone is connected represents the same place for the user.
	This implies:
		- if when the user was in gps1, he detected wifi wifix, and when he was in gps2 he detected the same wifix, => then gps1, gps2 represents the same place
		- if at time t1 the phone detected wifix and wifiy, and in the time t2, the phone detected wifiy and wifiz => then wifix, wifiy and wifiz represents the same place
		-if at time t1 the user detected wifix and was at place gps1, then at time t2 the user was connected to station s1 and was at place gps1, => then gps1, wifix and gps1 represents the same place
	NB: this is a first clustering step, other steps will be completed afterwards
	'''
	def cluster_locations(self):
		original_data = self.nontransformed_data
		
		original_wifi = original_data[self.wifi_feature]
		original_location = original_data[self.location_feature]
		original_station = original_data[self.station_feature]
		
		
		DateTimeUtils.start_chrono()
		#I- iteration over all the wi-fis seen
		gps_wifi={}
		gps_wifis_tmp={}
		station_wifi={}
		#contains the wifi_names that represent one cluster. cluster is represented as a set
		wifi_clusters = []
		
		
		#self.temp_check_mobile_wifi()
		wifi_gps_dict = self.regroup_location_and_station_with_wifi()
		wifi_clusters = self.regroup_concurrent_wifi(wifi_gps_dict)
		self.assign_numbers_to_clusters(wifi_clusters)
		#self.plot_wifi_time_distribution()
		
		self.stable_wifis = wifi_gps_dict.keys()
		
		

		
		for station, wifi in station_wifi.iteritems():
			if station not in self.station_locid:
				self.station_locid[station]=set()
			locid = self.wifi_locid[wifi]
			#listing all the location ids found for one gps coordinate will enable us to check that the relation is one to one => set contains only 1 element
			self.station_locid[station]=set.union(self.station_locid[station], set([locid]))
			
			#complete the metadata info
			if locid not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
				self.create_metadata_entry(locid)
			self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][locid]["station"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][locid]["station"], set([station]))
		
		
		#II- iterate over all the stations. The goal is to treat the stations that did not appear with a Wi-Fi app.
		DateTimeUtils.start_chrono()
		gps_station={}
		station_gps = {}
		#will need to work on copies
		original_location_copy = copy.deepcopy(original_location)
		for date, station in original_station.iteritems():
			station_coordinates = GpsUtils.to_string(station[self.station_lat], station[self.station_long])
			
			if station_coordinates not in self.station_locid:
				#this station has not seen before while iterating on the wifis
				if station_coordinates not in station_gps:
					station_gps[station_coordinates] = set()
					
				
				#get the gps that corresponds to the station sample (that occured in the same record) and mark them with it
				original_locations = DataExtractor.extract_realizations_in_time_range_soft_version_optimized_for_sorted_data_copy(original_location_copy, date)
				#original_locations = DataExtractor.extract_realizations_in_time_range_soft_version(original_location, date)
				#link all the gps locations with the station with who it occured
				for one_original_location in original_locations:
					gps_coordinates = GpsUtils.to_string(one_original_location[self.location_lat], one_original_location[self.location_long])
					
					if gps_coordinates not in gps_station:
						gps_station[gps_coordinates]=set()
					gps_station[gps_coordinates] = set.union(gps_station[gps_coordinates],set([station_coordinates]))
					station_gps[station_coordinates] = set.union(station_gps[station_coordinates], set([gps_coordinates]))
		
		#clustering the stations : two stations appearing with the same gps must be clustered together
		station_clusters = []
		for gps,stations in gps_station.iteritems():
			temp_clusters = []
			new_cluster = set(stations)
			for cluster in station_clusters:
				if len(set.intersection(cluster,new_cluster)) != 0:
					new_cluster = set.union(cluster,new_cluster)
				else:
					temp_clusters.append(cluster)
					
			temp_clusters.append(new_cluster)
			station_clusters = list(temp_clusters)
		
		
		#define the location id of the clusters of stations
		for cluster in station_clusters:
			#look for each cluster if any of the stations has a gps linked with it that already has a location id
			is_id_found=False
			loc_id_list=set()
			for station in cluster:
				gps_list = station_gps[station]
				
				for gps in gps_list:
					if gps in self.gps_locid:
						loc_id_list=set.union(loc_id_list,self.gps_locid[gps])
						is_id_found=True
				del station_gps[station]
			
			#otherwise add a new location id for that group
			if not is_id_found:
				loc_id_list= set([self.location_id])
				self.location_id+=1
				
			#assign the location_id to that group of stations
			for station in cluster:
				self.station_locid[station]=list(loc_id_list)
				
			#update the metadata information
			for loc_id in loc_id_list:
				if loc_id not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
					self.create_metadata_entry(loc_id)
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]["station"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]["station"], cluster)
				
		
		
		
		#define the location id for the stations that where not clustered
		for station, gps in station_gps.iteritems():
			if len(gps)==0:
				#only test for safety reasons, but this test should always be true. The stations with non empty gps where all removed above.
				self.station_locid[station]=set([self.location_id])
				
				#update the metadata information
				if self.location_id not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
					self.create_metadata_entry(self.location_id)
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][self.location_id]["station"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][self.location_id]["station"], set([station]))
				
				self.location_id+=1 
			else:
				raise Exception("Dictionary station_gps should only contain empty set values at this stage!!")
				
		#add the location id of the gps coordinates that corresponds to some stations
		for gps, stations in gps_station.iteritems():
			if gps not in self.gps_locid:
				self.gps_locid[gps]=set()
			locid_set = self.station_locid[next(iter(stations))]
			self.gps_locid[gps]=set.union(self.gps_locid[gps],locid_set)
			
			#complete the metadata info
			for locid in locid_set:
				if locid not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
					self.create_metadata_entry(locid)
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][locid]["gps"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][locid]["gps"], set([gps]))
		duration = DateTimeUtils.stop_chrono()
		print "station clustering "+str(duration)	
		
		
		#III- finally iterate over all the locations. The goal is to treat the locations that did not appear with a Wi-Fi and with Station.
		DateTimeUtils.start_chrono()
		for date, location in original_location.iteritems():
			gps_coordinates = GpsUtils.to_string(location[self.location_lat], location[self.location_long])
			
			if gps_coordinates not in self.gps_locid:
				self.gps_locid[gps_coordinates]=set([self.location_id])
				
				#complete the metadata info
				if self.location_id not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute]:
					self.create_metadata_entry(self.location_id)
				
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][self.location_id]["gps"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][self.location_id]["gps"], set([gps_coordinates]))
				
				self.location_id+=1
				
		#IV convert the metadata from sets to lists so that they can be written as json files
		for loc_id, meta_data in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].iteritems():
			meta_data["wifi"] = list(meta_data["wifi"])
			meta_data["gps"] = list(meta_data["gps"])
			meta_data["station"] = list(meta_data["station"])	
		
		
		duration = DateTimeUtils.stop_chrono()
		print "gps clustering "+str(duration)
		
		#V verifications tests
		#check that each gps and each station are mapped to exactly one location id
		self.location_unicity_check()
		
		#verify that each group of wifis that appear toghether have the same location id
		self.location_wifi_coherence_check()
			
			

	def create_metadata_entry(self, loc_id):
		self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]={}
		self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]["wifi"]=set()
		self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]["gps"]=set()
		self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][loc_id]["station"]=set()
		
	
	'''
	this method takes two transformed location features and merge them if:
		1- the two locations are the same
		2- the time difference between the last one and the next one is less than timeout_millis
	return the new time interval of the merged location, none if the merge was not possible
	
	last_location: int representing the id of the last location
	next_location: int representing the id of the next location
	'''
	def try_merge(self, t_interval_last_location, last_location, t_interval_next_location, next_location):
		#check that the time of the last location occurs before the time of the next location:
		if t_interval_last_location <= t_interval_next_location:
			time_interval = (long(DataExtractor.start_date_of_realization_in_millis(t_interval_next_location))-long(DataExtractor.end_date_of_realization_in_millis(t_interval_last_location)))
			last_location_id = last_location
			next_location_id = next_location
			if last_location_id == next_location_id  and time_interval <= LocationTransformer.timeout_millis:
				#concatenate the two realizations
				merged_interval = DataOperations.union_of_date_intervals_soft_version(t_interval_last_location,t_interval_next_location)
				
			else:
				#the two realizations wont be concatenated so write the last one
				merged_interval = None
					
			return merged_interval
		
		
		else:
			raise Exception("Wrong ordering : last location has time interval "+t_interval_last_location+" whereas next location has time "+t_interval_next_location)
			
	
	'''
	Input: 
			data: the current data that is being filled with the transformed location data.
			t_interval_last_location: the time interval of the last entry written in the data. None if we are in the first entry (there is no last yet)
			last_location: the id of the last location written in the data. None if we are in the first entry (there is no last yet)
			t_interval_next_location: the next location interval to be taken into account
			next_location: the next location to be taken into account
			
	Updates the data with the new entries (next location and next time interval): tries to merge with the last entry, otherwise create a new entry in the data
	for the new location
	
	Note: the locations should be put in the method in a sorted increasing time order
	
	return the interval that was added to the data
	'''
	def update_location_data(self, data, t_interval_last_location, last_location, t_interval_next_location, next_location):
		if t_interval_last_location == None:
			#first location: there is no previous location yet => write it in the data
			location_realization = {self.transformed_feature_location_attribute : next_location}
			data[t_interval_next_location] = location_realization
			return t_interval_next_location
				
		else:
			#there is a previous location => see if a merge is possible
			merged_interval = self.try_merge(t_interval_last_location, last_location, t_interval_next_location, next_location)
				
			if merged_interval == None:
				#merge not possible => write the current entry in the data
				location_realization = {self.transformed_feature_location_attribute : next_location}
				data[t_interval_next_location] = location_realization
				return t_interval_next_location
			else:
				#merge successful => replace the last entry in the data by the merged one
				if merged_interval != t_interval_last_location:
					#it may happen that the t_interval_next_location is completely contained in the t_interval_last_location and that the merged interval equals t_interval_last_location
					data[merged_interval] = data[t_interval_last_location]
					del data[t_interval_last_location]
				return merged_interval
				
				
	'''
	merge the two clusters indicated and returns the value of the new merged one
	'''
	def merge_clusters(self, id_cluster_mapper, first_id, second_id, do_check):
		#get the mapped values of the cluster given at input
		is_merge_possible = True
		mapped_first_id = self.find_mapped_cluster_id(id_cluster_mapper, first_id)
		mapped_second_id = self.find_mapped_cluster_id(id_cluster_mapper, second_id)
		old_cluster = self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_second_id]
		
		if mapped_first_id != mapped_second_id:
			#create the new cluter
			new_cluster = {"wifi": self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["wifi"] + old_cluster["wifi"],
							"gps": self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["gps"] + old_cluster["gps"],
							"station": self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["station"] + old_cluster["station"] }
			all_coordinates = new_cluster["gps"]+ new_cluster["station"]
			
			if do_check and (not GpsUtils.is_max_distance_less_or_equal_than(all_coordinates, LocationTransformer.max_cluster_distance_threshold)):
				is_merge_possible = False
			
			if is_merge_possible:
				#update the metadata info
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["wifi"]+=old_cluster["wifi"]
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["gps"]+=old_cluster["gps"]
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["station"]+=old_cluster["station"]
				
				if "center" in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id] and "center" in old_cluster:
					#update the new center and the new radius of new merged cluster.
					#if it is the case, then the clusters represent cercle with a certain radius a long a the center point. Thus the new center will only
					#be computed taking into acocount the centers and the radius. It is not a the center computed using the gps points. The gps points are there just for indication.
					
					
					bari_dist = GpsUtils.distance_from_str(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["center"], old_cluster["center"])
					radius1 = self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["radius"]
					center1= self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["center"]
					radius2= old_cluster["radius"]
					center2= old_cluster["center"]
					#We have three cases:
					if bari_dist <= radius1 and radius1 >= radius2:
						#1- the circle 2 is completely contained in the circle 1
						#here the radius and the baricenter are the ones of the circle 1
						baricenter = center1
						radius = radius1
					
					elif bari_dist <= radius2 and radius2 >= radius1:
						#2- the circle 1 is completely contained in the circle 2
						#here the radius and the baricenter are the ones of the circle 2
						baricenter = center2
						radius = radius2
					
					elif bari_dist> radius1 and bari_dist > radius2:
						#3- the two circles intersect each other in some portion
						#the new center is selected to be the point that will result in the smallest radius so that the circles 1 and 2 are contained in it. 
						#Let's consider the line that lies the two centers and that stops at the border of each circle. The new center is the middle of this line
						# and the radius is then the length of this line / 2 => r1+dist(center1,center2)+r2
						#the coordinates of the center will be computed using the ones of of the circle 1 and circle 2 and some weights. Those weights represent the 
						#importance of center 1 with respect to center 2.
						#let inter be the distance where the two radius intersects, the wights are the following: w1 = (r1-(inter/2)), w2 = (r2-(inter/2))
						inter = (radius1+radius2)-bari_dist
						baricenter = GpsUtils.baricenter([center1, center2], [(radius1-(inter/2)), (radius2-(inter/2))])
						radius = (radius1+bari_dist+radius2)/2.0
						
					else:
						#should never happen
						raise Exception("UNEXPECTED BRANCH EXCEPTION")
					
					self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["center"]= baricenter
					self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id]["radius"] = radius
					
					
				
				elif not("center" not in self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_first_id] and "center" not in old_cluster):
					raise Exception("INVALID CLUSTERS STATE EXCEPTION: trying to merge one cluster represented as a center and radius and the other represented as a set of points")
					
					
						
					
				
					
				#remove the old cluster from the metadata
				del self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][mapped_second_id]
				
			
				#map the second id to the first_id
				self.update_mapper_cluster_id(id_cluster_mapper, mapped_second_id, mapped_first_id)
				
			else:
				return -1
		return mapped_first_id
	
	'''
	if the id of the clusters are not all successive (ex: we have id 1, 2, and then 4) transforms the ids to all successive number (ex: adds the cluster 3)
	input: [] a dictionary that represents the mapping of the old ids with respect to the new ones. Key is an old cluster id, value is a new cluster id
	this dictionary will be completed with the new mapped values
	'''
	def make_cluster_numbers_successive(self, id_cluster_mapper):
		ordered_ids = sorted(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute].keys())
		new_id = 0
		
		for id in ordered_ids:
			if id > new_id:
				#change the id of the cluster
				self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][new_id]=self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][id]
				del self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][id]
				self.update_mapper_cluster_id(id_cluster_mapper, id, new_id)
			elif id<new_id:
				#should never be the case
				raise Exception ("Unexprected branch: id "+str(id)+" < new_id "+str(new_id))
			new_id+=1
	
	'''
	Given a cluster id mapper and an olde cluster_id returns the new cluster id to which is mapped the old cluster_id
	'''
	def find_mapped_cluster_id(self, cluster_id_mapper, cluster_id):
		if cluster_id in cluster_id_mapper:
			return cluster_id_mapper[cluster_id]
		else:
			return cluster_id
	
	
	def update_mapper_cluster_id(self, id_cluster_mapper, old_cluster_id, new_cluster_id):
		for key, mapped_id in id_cluster_mapper.iteritems():
			if mapped_id == old_cluster_id:
				id_cluster_mapper[key]=new_cluster_id
				
		id_cluster_mapper[old_cluster_id]=new_cluster_id
				
	

			
	def is_wifi_stable_function (self, max_distance, nb_days_observation):
		result = math.floor((LocationTransformer.max_wifi_range_in_meters+1)/((max_distance+1)*1.0))*math.floor((nb_days_observation*1.0)/LocationTransformer.min_days_of_observed_wifi)
		
		if result == 0:
			return False
		else:
			return True
			
	
	'''
	regroup each wifi with the set of the gps points seen in the same time than him. the gps points come from the location and the station
	also selects only the wifis that are stable with respect to the gps locations (remove the mobile wifis as the connexion sharing, the internal lans)
	
	return a dict where the keys are the wifi names and the values are the gps points linked to it.
	Format: {wifi : {gps: [...]},
					{station: [...]}}
	'''
	def regroup_location_and_station_with_wifi(self):
		original_data = self.nontransformed_data
		original_wifi = original_data[self.wifi_feature]
		original_location = original_data[self.location_feature]
		original_station = original_data[self.station_feature]
		
		
		wifi_gps_days = {}
		
		#will need to work on copies
		original_location_copy = copy.deepcopy(original_location)
		original_station_copy = copy.deepcopy(original_station)
		iter_num = 0
		for date, wifis in original_wifi.iteritems():
			iter_num += 1
			print "selecting stable wifis step 1 in progress: iteration "+str(iter_num)+" / "+str(len(original_wifi))
			
			#get the locations seen at the same time and transform them to gps points
			concurrent_original_locations = DataExtractor.extract_realizations_in_time_range_soft_version_optimized_for_sorted_data_copy(original_location_copy, date)
			concurrent_gps_locations = {GpsUtils.to_string(one_original_location[self.location_lat], one_original_location[self.location_long]) for one_original_location in concurrent_original_locations}
			
			#get the stations seen at the same time and transform them to gps points
			concurrent_original_stations = DataExtractor.extract_realizations_in_time_range_soft_version_optimized_for_sorted_data_copy(original_station_copy, date)
			concurrent_gps_stations = {GpsUtils.to_string(one_original_station[self.station_lat], one_original_station[self.station_long]) for one_original_station in concurrent_original_stations}
			
		
			
			
			#if there is no gps associated, no update to do
			if (len(concurrent_gps_locations)+len(concurrent_gps_stations))>0:
				#for each wifi add those gps to his concurrent gps entries
				date_no_time = DataOperations.build_date_with_default_time_no_millis(date)
				for wifi in wifis:
					wifi_name = wifi[self.wifi_name]
					if wifi_name not in wifi_gps_days:
						#create an entry for this new seen wifi
						wifi_gps_days[wifi_name]={}
						wifi_gps_days[wifi_name]["gps"]=set() #contains the set of gps that comes from a location
						wifi_gps_days[wifi_name]["station"]= set() #contains the set of gps that comes from a station
						wifi_gps_days[wifi_name]["last_date"]= date #contains the last date in which this wifi was seen					
						wifi_gps_days[wifi_name]["nb_seen_days"]=1 #contains the number of different days where a wifi was observed with a location
					
					#taking into account the current date and the last date compute new number of days covered by the current_date
					intersection = DataOperations.intersection_of_date_intervals_day_precision(date , wifi_gps_days[wifi_name]["last_date"])
					
					if intersection != None:
						#we take into account the additional days
						additional_covered_days = DataOperations.days(DataOperations.substraction_of_date_intervals_soft_version_day_precision(date,intersection))-1 
					else:
						additional_covered_days = DataOperations.days(date)
					
					wifi_gps_days[wifi_name]["last_date"]= date
					wifi_gps_days[wifi_name]["nb_seen_days"] += additional_covered_days
					
					#add the concerned wifis and stations
					wifi_gps_days[wifi_name]["gps"]=set.union(wifi_gps_days[wifi_name]["gps"], concurrent_gps_locations)
					wifi_gps_days[wifi_name]["station"]= set.union(wifi_gps_days[wifi_name]["station"], concurrent_gps_stations)
					
		
		#select the stable wifis => the ones that appear always in places that are close to each others
		wifi_gps = {}
		iter_num = 0
		for wifi_name, gps_days in wifi_gps_days.iteritems():
			iter_num += 1
			print "selecting stable wifis step 2 in progress: iteration "+str(iter_num)+" / "+str(len(wifi_gps_days))
			gps_points = set.union(gps_days["gps"],gps_days["station"])
			
			#compute the maximum distance that separates two points in this set of gps points
			[max_distance,extreme_point_1,extreme_point_2,baricenter] = GpsUtils.max_distance_upperbound (gps_points)
			nb_days_observation = gps_days["nb_seen_days"]
			
			if self.is_wifi_stable_function (max_distance, nb_days_observation):
				wifi_gps[wifi_name] = {}
				wifi_gps[wifi_name]["gps"]=gps_days["gps"]
				wifi_gps[wifi_name]["station"]= gps_days["station"]
				wifi_gps[wifi_name]["extreme_point_1"]=extreme_point_1
				wifi_gps[wifi_name]["extreme_point_2"] = extreme_point_2
				wifi_gps[wifi_name]["baricenter"] = baricenter
				
		print "we selected "+str(len(wifi_gps))+" from a total set of "+str(len(wifi_gps_days))
		return wifi_gps
			
			
	'''
	regroups the wifis that appeared together in the same clusters. Verifies that the clusters do not exceed the allowed distance.
	'''	
	def regroup_concurrent_wifi(self, wifi_gps):
		print "begin regrouping concurrent wifis"
		original_data = self.nontransformed_data
		original_wifi = original_data[self.wifi_feature]
		wifi_clusters = {}
		iter_num = 1
		for date, wifis in original_wifi.iteritems():
			print "regrouping concurrent wifis in progress : iteration "+str(iter_num)+" from "+str(len(original_wifi))
			iter_num+=1
			#select the names of the stable concurrent wifis. Those wifis appeared together so they are a potential cluster
			wifi_names = {wifi[self.wifi_name] for wifi in wifis if wifi[self.wifi_name] in wifi_gps}
			
			#check that at least we have one stable wifi selected
			if len(wifi_names)>0:
				#select all the coordinates of the different wifis
				gps_points_union = set()
				station_points_union = set()
				
				for wifi_name in wifi_names:
					gps_points_union = set.union(gps_points_union,wifi_gps[wifi_name]["gps"])
					station_points_union = set.union(station_points_union, wifi_gps[wifi_name]["station"] )
						
				
				all_points_union = set.union(gps_points_union, station_points_union)
				
				[max_distance_upperbound, extreme_point_1, extreme_point_2, baricenter] = GpsUtils.max_distance_upperbound(gps_points_union)
				
				if max_distance_upperbound > LocationTransformer.max_cluster_distance_threshold:
					#check if the real distance really exceeds the threshold
					[max_distance, extreme_point_1, extreme_point_2, baricenter]  = GpsUtils.max_distance(gps_points_union, 0)
					
					if max_distance> LocationTransformer.max_cluster_distance_threshold:
						#the union of those points results in a too far points. So this group of Wifi do not represent a cluster
						raise Exception( "the group "+str(wifi_names)+" appeared together but has upperbound max distance "+str(max_distance)+" so it do not represent a cluster \n complete realization : "+JsonUtils.dict_as_json_str(wifis))
				else:
					#the union of those points result in a cluster. So see if this cluster intersects others
					
					current_clusters = wifi_clusters.keys()
					new_cluster_points = {"gps" : gps_points_union,
										"station": station_points_union,
										"baricenter": baricenter,
										"extreme_point_1": extreme_point_1,
										"extreme_point_2": extreme_point_2}
					new_cluster_wifis = list(wifi_names)
					
					for cluster in current_clusters:
						#if the intersection is equal to 0 it means that there is any common element between the current set of names and the considered cluster. Thus, there is any merge possible.
						if len(set.intersection(set(self.list_from_string(cluster)), set(new_cluster_wifis))) != 0:
							#look if the max_distance between the two clusters allow us to merge
							union_clusters_gps_points = set.union(new_cluster_points["gps"], wifi_clusters[cluster]["gps"] )
							union_clusters_station_points = set.union(new_cluster_points["station"],wifi_clusters[cluster]["station"])
							union_clusters_all_points = set.union(union_clusters_gps_points, union_clusters_gps_points)
							
							if len(set(self.list_from_string(cluster))) == len(set.union(set(self.list_from_string(cluster)), set(new_cluster_wifis))):
								#if the len of union of the two group of clusters is equal to the length of the cluster, it means that no new element will be added to the cluster, and the whole cluster already exists.
								#no need to compute again [inter_cluster_distance, union_extreme_point_1, union_extreme_point_2, union_baricenter
								[inter_cluster_distance, union_extreme_point_1, union_extreme_point_2, union_baricenter] = list([0, wifi_clusters[cluster]["extreme_point_1"], wifi_clusters[cluster]["extreme_point_2"],wifi_clusters[cluster]["baricenter"]])
							else:
								[inter_cluster_distance, union_extreme_point_1, union_extreme_point_2, union_baricenter]  = GpsUtils.max_distance_upperbound(union_clusters_all_points)
							
							if inter_cluster_distance <= LocationTransformer.max_cluster_distance_threshold:
								#do the merge
								new_cluster_points["gps"] = union_clusters_gps_points
								new_cluster_points["station"] = union_clusters_station_points
								new_cluster_points["extreme_point_1"] = union_extreme_point_1
								new_cluster_points["extreme_point_2"] = union_extreme_point_2
								new_cluster_points["baricenter"] = union_baricenter
								new_cluster_wifis = list(set.union(set(new_cluster_wifis), set(self.list_from_string(cluster))))
								del wifi_clusters[cluster]
							else:
								#compute the real distance and not an upperbound
								[real_inter_cluster_distance, union_extreme_point_1, union_extreme_point_2, union_baricenter]  = GpsUtils.max_distance(union_clusters_all_points, LocationTransformer.max_cluster_distance_threshold)
								if real_inter_cluster_distance <= LocationTransformer.max_cluster_distance_threshold:
									#do the merge
									new_cluster_points["gps"] = union_clusters_gps_points
									new_cluster_points["station"] = union_clusters_station_points
									new_cluster_points["extreme_point_1"] = union_extreme_point_1
									new_cluster_points["extreme_point_2"] = union_extreme_point_2
									new_cluster_points["baricenter"] = union_baricenter
									
									new_cluster_wifis = list(set.union(set(new_cluster_wifis), set(self.list_from_string(cluster))))
									del wifi_clusters[cluster]
									
								else:
									raise Exception("cannot merge "+str(wifi_names)+" and "+str(cluster)+" because their distance is "+str(real_inter_cluster_distance)+" and the upperbound is "+str(inter_cluster_distance))
						
					wifi_clusters[self.list_to_string(sorted(new_cluster_wifis))]=new_cluster_points

		return wifi_clusters
	


	
	'''
	attributes to each cluster of wifi groups and points and id that will represent the id of the location.
	updates the metadata information with this cluster id and also the wifi_locid, gps_locid and station_locid dictionaries
	'''
	def assign_numbers_to_clusters(self, wifi_clusters):
		print "begin assiging numbers"
		for wifi_cluster_str, points in wifi_clusters.iteritems():
			wifi_cluster = self.list_from_string(wifi_cluster_str)
			cluster_id = self.location_id
			self.location_id +=1
			
			#assign to each wifi his location id
			for wifi in wifi_cluster:
				self.wifi_locid[wifi]=cluster_id
			
			#assign to each gps his location id
			for gps in points["gps"]:
				if gps not in self.gps_locid:
					self.gps_locid[gps]=set()
				self.gps_locid[gps] = set.union(self.gps_locid[gps], set([cluster_id]))
			
			#assign to each station his location id
			for station in points["station"]:
				if station not in self.station_locid:
					self.station_locid[station] = set()
				self.station_locid[station]=set.union(self.station_locid[station],set(cluster_id))
			
			#update the metadata information
			self.create_metadata_entry(cluster_id)
			self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][cluster_id]["wifi"]=wifi_cluster
			self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][cluster_id]["gps"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][cluster_id]["gps"], points["gps"])
			self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][cluster_id]["station"]=set.union(self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][cluster_id]["station"], points["station"])
		
	def plot_wifi_time_distribution(self):
		location_count = {}
		original_data = self.nontransformed_data
		original_wifi = original_data[self.wifi_feature]
		iter = 0
		for date, wifis in original_wifi.iteritems():
			print "iteration "+str(iter)+" from "+str(len(original_wifi))
			iter+=1
			#select the names of the stable concurrent wifis. Those wifis appeared together so they are a potential cluster
			wifi_names = [wifi[self.wifi_name] for wifi in wifis if wifi[self.wifi_name] in self.wifi_locid]
			if len(wifi_names)>0:
				location = self.wifi_locid[wifi_names[0]]
				
				if location not in location_count:
					location_count[location] = np.zeros(24)
				
				if DataExtractor.start_date_of_realization(date).weekday()>= 5 and DataExtractor.start_date_of_realization(date).weekday()<= 6:
					#it is a week day so we count it
					hour_start = DataExtractor.start_date_of_realization(date).hour
					hour_end = DataExtractor.end_date_of_realization(date).hour
					
					location_count[location][hour_start:hour_end+1]=location_count[location][hour_start:hour_end+1]+1
				
			
			
		
		
		
		
		np_matrix = np.zeros((len(location_count.keys()), 24))
		idex = 0
		for location in location_count.keys():
			np_matrix[idex,:]=location_count[location]
			idex+=1
			
		#create the distribution of time by location
		row_sums = np_matrix.sum(axis=1)
		time_dist = np_matrix / row_sums[:, np.newaxis]
		td_title = "distribution of hours by wifi_cluster week days"
		td_x = "hours"
		td_y = "Pr[hour|cluster]"


		#create the distribution of locations by hour
		column_sums = np_matrix.sum(axis=0)
		location_dist = np_matrix / column_sums[np.newaxis , :]
		ld_title = "distribution of wifi_clusters by hour week ends"
		ld_x = "hours"
		ld_y = "Pr[cluster|hour]"

		
		#create the legends
		legends = [self.transformed_feature_metadata[LocationTransformer.transformed_feature_location_attribute][location]["wifi"][0] for location in location_count.keys()]
		
		PlotlibDrawer.plot_np(None, time_dist, legends, td_x, td_y, td_title, 0)	
		PlotlibDrawer.plot_np(None, location_dist, legends, ld_x, ld_y, ld_title, 0)
		PlotlibDrawer.show()
			
	def list_from_string(self, str):
		return JsonUtils.json_str_as_dict(str)
		
	def list_to_string(self, one_list):
		return JsonUtils.dict_as_json_str(list(one_list))
				
		
		
		
	
					
							
				
		