'''
This file contains utils operations concerning the GPS points (latitude, longitude)
'''
#!/usr/bin/env python

from math import radians, cos, sin, asin, sqrt, pi, atan2

import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils

class GpsUtils:
	# the separator used in the string representation to separate between the latitude and the longitude
	separator =" , "

	'''
	return the string representation a gsp coordinate (latitude, longitude) pair
	'''
	@staticmethod
	def to_string(latitude, longitude):
		return str(latitude)+GpsUtils.separator+str(longitude)
		
	'''
	return the latitude from a string representation of gps coordinates
	'''
	@staticmethod
	def get_latitude_from_string(gps_str):
		return float(gps_str.split(GpsUtils.separator)[0])
	
	'''
	return the longitude from a string representation of gps coordinates
	'''
	@staticmethod	
	def get_longitude_from_string(gps_str):
		return float(gps_str.split(GpsUtils.separator)[1])
		
		
	'''
	return the distance in meters between two points in the earth expressed as latitude, longitude coordinates
	'''
	@staticmethod
	def distance(lat1, lon1, lat2,  lon2):
		"""
		Calculate the great circle distance between two points 
		on the earth (specified in decimal degrees)
		"""
		# convert decimal degrees to radians 
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
		# haversine formula 
		dlon = lon2 - lon1 
		dlat = lat2 - lat1 
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
		c = 2 * asin(sqrt(a)) 
		km = 6367 * c
		m = km*1000
		return m
		
		
		
	
	'''
	return the distance in meters between two points in the earth expressed as latitude, longitude coordinates
	'''
	@staticmethod	
	def distance_from_str(str_gps_1 , str_gps_2):
		return GpsUtils.distance(GpsUtils.get_latitude_from_string(str_gps_1), GpsUtils.get_longitude_from_string(str_gps_1), GpsUtils.get_latitude_from_string(str_gps_2),  GpsUtils.get_longitude_from_string(str_gps_2))
		
	
	'''
	return the coordinates of the exact baricenter as a string gps point (latitude,longitude)
	when weights = None than a normal center is computed assuming that the weights are equal to one
	'''
	@staticmethod	
	def baricenter(str_gps_points, weights):
		if weights == None:
			weights = [1 for i in range(0, len(str_gps_points))]
			
		if len(weights) != len(str_gps_points):
			raise Exception("NON MATCHING ARGUMENT EXCEPTION: there is "+str(len(str_gps_points))+" points and "+str(len(weights))+" coefficients ")
			
		if len(str_gps_points)==0:
			raise Exception("Empty array Exception: the array given as input is empty")
	
		str_gps_points_list = list(str_gps_points)
		baricenter_lat = 0
		baricenter_long = 0
		
		
		#compute the baricenter
		w = 0
		tot_weights = 0.0
		for str_gps in str_gps_points_list:
			baricenter_lat += (weights[w]*GpsUtils.get_latitude_from_string(str_gps))
			baricenter_long += (weights[w]*GpsUtils.get_longitude_from_string(str_gps))
			tot_weights += weights[w]
			w+=1
		
		baricenter_lat = baricenter_lat/tot_weights
		baricenter_long = baricenter_long / tot_weights
		baricenter = GpsUtils.to_string(baricenter_lat, baricenter_long)
		return baricenter
		
		
		
		
		
		
	'''
	computes the maximum distance that separate an array of gps entries.
	
	NB: the array of gps entries str_gps_points is an array of gps points written in the string format
	
	if the threshold is > 0, then if the max distance exceeds this threshold, then the loop is stopped in the current
	
	return [max_distance,extreme_point_1,extreme_point_2,baricenter] where extreme_point are the points the have max_distance and baricenter is the center of the array
	'''
	@staticmethod
	def max_distance (str_gps_points, threshold):
		if len(str_gps_points)==0:
			raise Exception("Empty array Exception: the array given as input is empty")
		
		str_gps_points_list = list(str_gps_points)
		baricenter_lat = 0
		baricenter_long = 0
		max_distance = 0
		extreme_point_1 = None
		extreme_point_2 = None
		#Warning: do not iterate from i-> range(0, len(str_gps_points)-1) and j -> range(i+1, len(str_gps_points)) because baricenter will ignore the last value
		for i in range(0,len(str_gps_points_list)):
			str_gps_1 = str_gps_points_list[i]
			baricenter_lat += GpsUtils.get_latitude_from_string(str_gps_1)
			baricenter_long += GpsUtils.get_longitude_from_string(str_gps_1)
			for j in range(i, len(str_gps_points_list)):
				str_gps_2 = str_gps_points_list[j]
				dist = GpsUtils.distance(GpsUtils.get_latitude_from_string(str_gps_1), GpsUtils.get_longitude_from_string(str_gps_1), GpsUtils.get_latitude_from_string(str_gps_2),  GpsUtils.get_longitude_from_string(str_gps_2))
				if dist> max_distance:
					max_distance = dist
					extreme_point_1 = str_gps_1
					extreme_point_2 = str_gps_2
					
				if max_distance>threshold and threshold>0:
					return [max_distance,extreme_point_1,extreme_point_2,None]
		
		baricenter_lat = baricenter_lat/len(str_gps_points_list)
		baricenter_long = baricenter_long / len(str_gps_points_list)
		baricenter = GpsUtils.to_string(baricenter_lat, baricenter_long)
		return [max_distance,extreme_point_1,extreme_point_2,baricenter]
		
	
	'''
	returns true if the maximum distance that separates an array of gps is less or equal than threshold
	'''
	@staticmethod
	def is_max_distance_less_or_equal_than(str_gps_points, threshold):
		if len(str_gps_points)==0:
			raise Exception("Empty array Exception: the array given as input is empty")
	
		#we prefer first to rely on an upperbound because the upperbound runs in O(n) while the real max distance runs in O(n^2)
		[upperbound, extreme_point, second_extreme_point, baricenter] = GpsUtils.max_distance_upperbound (str_gps_points)
		if upperbound <= threshold:
			#the upperbound of the maximum distance is smaller than the threshold so the extact maximum distance is also smaller than the threshold
			return True
		
		else:
			#compute the real maximum distance and compare it to the threshold
			[max_distance,extreme_point_1,extreme_point_2,baricenter] = GpsUtils.max_distance (str_gps_points, threshold)
			print "upperbound is "+str(upperbound)+" and maxdistance is "+str(max_distance)
			#NB: if threshold > 0 it may happen that upperbound > max_distance. This is because upperbound method stopped when it has exceeded the threshold and ended up with
			#a value smaller than the max distance
			if max_distance <=threshold:
				return True
			else:
				return False
			
		
	
	'''
	return the maximum distance that separate an array of gps entries from his baricenter (=center).
	it also stores the two points that resulted in the maximum distance in extreme_point_1, extreme_point_2
	
	NB: the array of gps entries str_gps_points is an array of gps points written in the string format
	
	if the threshold is > 0, then if the max distance exceeds this threshold, then the loop is stopped and the current results are returned
	
	
	return [max_distance, second_max_distance, extreme_point, second_extreme_point, baricenter] where extreme_point is the farest point from the baricenter and baricenter is the center of the array.
	second_extreme_point and second_max_distance are respectively the distance and the point of the second farest point from the baricenter
	'''
	@staticmethod
	def max_distance_to_baricenter(str_gps_points, threshold):
		if len(str_gps_points)==0:
			raise Exception("Empty array Exception: the array given as input is empty")
	
		str_gps_points_list = list(str_gps_points)
		baricenter_lat = 0
		baricenter_long = 0
		
		
		#compute the baricenter
		for str_gps in str_gps_points_list:
			baricenter_lat += GpsUtils.get_latitude_from_string(str_gps)
			baricenter_long += GpsUtils.get_longitude_from_string(str_gps)
		
		baricenter_lat = baricenter_lat/len(str_gps_points_list)
		baricenter_long = baricenter_long / len(str_gps_points_list)
		baricenter = GpsUtils.to_string(baricenter_lat, baricenter_long)
		
		#compute the farest distance from the baricenter
		max_distance = 0
		second_max_distance = 0
		second_extreme_point = None
		extreme_point = None
		for str_gps in str_gps_points_list:
			dist = GpsUtils.distance(GpsUtils.get_latitude_from_string(str_gps), GpsUtils.get_longitude_from_string(str_gps), baricenter_lat,  baricenter_long)
			if dist>= max_distance:
				#check the farest point and distance and update the second farest ones
				second_max_distance = max_distance
				second_extreme_point = extreme_point
				max_distance = dist
				extreme_point = str_gps
				
			'''
			if dist>second_max_distance and dist<max_distance:
				#check the second farest point and distance
				second_max_distance = dist
				second_extreme_point = str_gps
			'''	
					
			if max_distance>threshold and threshold>0:
				return [max_distance+second_max_distance, extreme_point, second_extreme_point, None]
		
		
		
		return [max_distance, second_max_distance, extreme_point, second_extreme_point, baricenter]
	
	'''
	gives an upper-bound of the maximum distance that separates two points in a set of points (cluster).
	Let's call d this distance and max_dist(bari) the distance that separates the farest point of the cluster from the baricenter of the cluster and second_max_distance the second largest distance
	and max_point the farest point and second_max_point the second farest. Then the following inequality holds:
		d<= (max_dist(bari)+second_max_dist(bari))
	this how the upper-bound is computed
	
	returns [upper_bound_distance, extreme_point, second_extreme_point, baricenter]
	'''
	@staticmethod	
	def max_distance_upperbound (str_gps_points):
		if len(str_gps_points)==0:
			raise Exception("Empty array Exception: the array given as input is empty")
	
		[max_distance, second_max_distance, extreme_point, second_extreme_point, baricenter] = GpsUtils.max_distance_to_baricenter(str_gps_points,0)
		
		upperbound =(max_distance+second_max_distance)
		return [upperbound, extreme_point, second_extreme_point, baricenter]
	
	'''
	compute the baricenter of two clusters given their baricenter and their respective size.
	baricenter = [(baricenter1*size1)+(baricenter2*size2)]/(size1*size2)
	return the baricenter of the two clusters
	'''
	@staticmethod
	def compute_baricenter_of_two_clusters(cluster1_baricenter, cluster1_size, cluster2_baricenter, cluster2_size):
		new_baricenter_lat = (GpsUtils.get_latitude_from_string(cluster1_baricenter)*cluster1_size)+(GpsUtils.get_latitude_from_string(cluster2_baricenter)*cluster2_size)/(cluster1_size*cluster2_size)
		new_baricenter_long = (GpsUtils.get_longitude_from_string(cluster1_baricenter)*cluster1_size)+(GpsUtils.get_longitude_from_string(cluster2_baricenter)*cluster2_size)/(cluster1_size*cluster2_size)
		return GpsUtils.to_string(new_baricenter_lat, new_baricenter_long)
		
	'''
	gives an upper-bound of the maximum distance that separates two points in a set of two clusters.
	Let's call d this distance and max_dist(bari_i, point_i) the distance that separates the farest point of cluster i from the baricenter of cluster i:
		d<= max_dist(bari_1, point_1)+max_dist(bari_2, point_2)+dist(bari_1,bari_2)
	this how the upper-bound is computed
	
	returns the upperbound and stores the baricenter of the union of this two clusters so as the two extreme points of the union of those two clusters.
	those values are stored in common_extreme_point_1, common_extreme_point_2, common_baricenter
	'''
	@staticmethod	
	def inter_cluster_max_distance_upperbound(first_str_gps_points, first_extreme_point_1, first_extreme_point_2, baricenter_1, second_str_gps_points, second_extreme_point_1, second_extreme_point_2, baricenter_2):
		common_extreme_point_1 = None
		common_extreme_point_2 = None
		common_baricenter = None
		#compute the upperbound										
		first_cluster_max_radius = max(GpsUtils.distance(GpsUtils.get_latitude_from_string(first_extreme_point_1), GpsUtils.get_longitude_from_string(first_extreme_point_1), GpsUtils.get_latitude_from_string(baricenter_1),  GpsUtils.get_longitude_from_string(baricenter_1)),
								   GpsUtils.distance(GpsUtils.get_latitude_from_string(first_extreme_point_2), GpsUtils.get_longitude_from_string(first_extreme_point_2), GpsUtils.get_latitude_from_string(baricenter_1),  GpsUtils.get_longitude_from_string(baricenter_1)))
								   
		second_cluster_max_radius = max(GpsUtils.distance(GpsUtils.get_latitude_from_string(second_extreme_point_1), GpsUtils.get_longitude_from_string(second_extreme_point_1), GpsUtils.get_latitude_from_string(baricenter_2),  GpsUtils.get_longitude_from_string(baricenter_2)),
								   GpsUtils.distance(GpsUtils.get_latitude_from_string(second_extreme_point_2), GpsUtils.get_longitude_from_string(second_extreme_point_2), GpsUtils.get_latitude_from_string(baricenter_2),  GpsUtils.get_longitude_from_string(baricenter_2)))
		
		inter_baricenter_distance = GpsUtils.distance(GpsUtils.get_latitude_from_string(baricenter_1), GpsUtils.get_longitude_from_string(baricenter_1), GpsUtils.get_latitude_from_string(baricenter_2),  GpsUtils.get_longitude_from_string(baricenter_2))
		
		max_distance_upper_bound = first_cluster_max_radius+second_cluster_max_radius+inter_baricenter_distance
		
		
		#compute the common baricenter
		common_baricenter = GpsUtils.compute_baricenter_of_two_clusters(baricenter_1, len(first_str_gps_points), baricenter_2, len(second_str_gps_points))
		
		#compute the new extreme points
		potential_extreme_points = [first_extreme_point_1, first_extreme_point_2, second_extreme_point_1, second_extreme_point_2]
		useless_baricenter = None
		[extreme_points_max_dist,common_extreme_point_1, common_extreme_point_2, useless_baricenter] = GpsUtils.max_distance(potential_extreme_points, 0)
		
		if extreme_points_max_dist>max_distance_upper_bound:
			raise Exception("found max distance bigger than the upperbound computed")
			
		return [extreme_points_max_dist,common_extreme_point_1, common_extreme_point_2, useless_baricenter]
					