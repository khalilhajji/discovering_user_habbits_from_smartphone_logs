'''
For now it just tests if there is clusters that overlaps
'''
#!/usr/bin/env python
import sys
import json
import os
import datetime
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from categorized_data_utils import *
from date_time_utils import *
from json_utils import *
from plot_lib_utils import *
from numpy_utils import *
from logs_file_writer import LogsFileWriter
from gps_utils import GpsUtils

#represents the number of locations that we choose to display. we display the k-most frequent locations
k = 20
def geographic_plot_one_user(user_id):
	
	complete_data = DataExtractor.load_json_data(user_id)
	location_data = collections.OrderedDict(sorted(DataExtractor.data(DataExtractor.location_name, complete_data).items()))
	location_metadata = DataExtractor.metadata(DataExtractor.location_name, complete_data)
	
	clusters = location_metadata[DataExtractor.location_attribute]
	overlapping_nb = 0
	iter = 0
	for cluster_id , cluster in clusters.iteritems():
		print "iteration "+str(iter)+" from "+str(len(location_metadata[DataExtractor.location_attribute]))
		iter+=1
		for cluster_two_id, cluster_two in clusters.iteritems():
			if cluster_id != cluster_two_id and "center" in cluster and "center" in cluster_two:
				distance = GpsUtils.distance_from_str(cluster[DataExtractor.location_metacenter],cluster_two[DataExtractor.location_metacenter])
				if distance <= (cluster[DataExtractor.location_metaradius] + cluster_two[DataExtractor.location_metaradius]):
					overlapping_nb+=1
					
	
	print overlapping_nb
	overlapping_nb = overlapping_nb/2
	
	print "the number of overlapping clusters is "+str(overlapping_nb)
			
		
		
		
		
		
		
		
		
		
		

		
		
		