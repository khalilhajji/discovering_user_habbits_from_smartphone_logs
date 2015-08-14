'''
plots the distribution of the number of visitis that the user userid made by location.


NOTE: we consider a visit the fact that the user was in a some place in a given hour. It means that if we have two realizations of the same place in the same hour of
the same day we count it only once

NOTE2: we represent those counts as a cumulative distribution (i.e number of locations visited at least x times)
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
def location_visits_distribution_one_user(user_id):
	
	complete_data = DataExtractor.load_json_data(user_id)
	location_data = collections.OrderedDict(sorted(DataExtractor.data(DataExtractor.location_name, complete_data).items()))
	location_metadata = DataExtractor.metadata(DataExtractor.location_name, complete_data)
	
	
	#contains the total number of visits for each location
	location_freq = {}
	
	iter = 0
	
	#this is to guarantee that we do not mark the same date more than ones (because it may occur that different realizations be mapped to the same hour)
	most_recent_date = None
	most_recent_location = None
	for date, location_feature in location_data.iteritems():
		print "iteration "+str(iter)+" from "+str(len(location_data))
		iter+=1
		
		location = location_feature[DataExtractor.location_attribute]
		if location not in location_freq:
			location_freq[location] = 0
		
		start_date = DataExtractor.start_date_of_realization(date)
		end_date = DataExtractor.end_date_of_realization(date)
		#get a list of datetimes representing the each hour covered between start date and end date
		hours_covered = DateTimeUtils.hours_between(start_date, end_date)
		
		
		#increment by 1 the concerned hours for location
		for datetime in hours_covered:
			if datetime != most_recent_date or location != most_recent_location:
				#then we have either a new date to mark or a new location
				location_freq[location]+=1
				most_recent_date = datetime
				most_recent_location = location
	#order the location_count by the most frequent locations
	location_freq = collections.OrderedDict(sorted(location_freq.items(), key=lambda tup: tup[1], reverse=True))
	
	#frequencies contains the frequencies of visits of each location sorted by deacreasing order ex: [10,5, 2,2,1,1,1]
	
	frequencies = np.asarray(location_freq.values())[0:k]
	
	
	#follow the example above: unique_freq = [1,2,5,10], counts = [3,2,1,1]
	unique_freq, counts = np.unique(frequencies, return_index=False, return_inverse=False, return_counts=True)
	#reverse the order of the arrays: unique_freq = [10,5,2,1], counts = [1,1,2,3] 
	unique_freq[:] = unique_freq[::-1]
	counts[:] = counts[::-1]
	
	#cumulative_counts = [1,2,4,7]
	cumulative_counts = np.cumsum(counts)
	
	
	
	title = "top-"+str(k)+" location visits cumulative distribution for user "+str(user_id)
	x_label = "number of locations x that were visited at least v times"
	y_label = "number of visits  v"
	
	
	PlotlibDrawer.plot_np_simple(None, cumulative_counts, unique_freq, x_label, y_label, title, 0, 'ro')
	
			
		
		
		
		
		
		
		
		
		
		

		
		
		
		