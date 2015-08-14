'''
plots the distribution of the locations of the given user per hour.

Moreover, it writes a file in the log dict containing the metadatinformation about each location (wifis, gps ..)
need to call PlotlibDrawer.show() to see the plot (this method is blocking)

NOTE: we are interested in knowing where the user goes in funciton of the time.
	Thus, if we see two realizations saying that the user was in place x in 10-10-2014 12PM, we count it only once.
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

#the option give the possibility to only take into account the week_days, or only the week_ends all very thing
options = ["week_end", "week_days", "all"]

#modify current option to change the option
hardcoded_option = "week_days"

#represents the number of locations that we choose to display. we display the k-most frequent locations
k = 10
def location_distribution_per_hour_one_user(user_id, option):
	
	if option!=None:
		current_option = option
	else:
		current_option = hardcoded_option
	
	complete_data = DataExtractor.load_json_data(user_id)
	location_data = collections.OrderedDict(sorted(DataExtractor.data(DataExtractor.location_name, complete_data).items()))
	location_metadata = DataExtractor.metadata(DataExtractor.location_name, complete_data)
	
	#contains the counts per hour for each location
	location_count = {}
	
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
		if location not in location_count:
			location_count[location] = np.zeros(24)
			location_freq[location] = 0.0
		
		start_date = DataExtractor.start_date_of_realization(date)
		end_date = DataExtractor.end_date_of_realization(date)
		#get a list of datetimes representing the each hour covered between start date and end date
		hours_covered = DateTimeUtils.hours_between(start_date, end_date)
		
		
		#increment by 1 the concerned hours for location
		for datetime in hours_covered:
			if datetime != most_recent_date or location != most_recent_location:
				#then we have either a new date to mark or a new location
				if ((current_option == options[0] and DateTimeUtils.is_week_end_day(datetime))
					or (current_option == options[1] and not DateTimeUtils.is_week_end_day(datetime))
					or (current_option == options [2])):
					#fits the options
					location_count[location][datetime.hour]+=1.0
					location_freq[location]+=1.0
				most_recent_date = datetime
				most_recent_location = location
	#order the location_count by the most frequent locations
	location_freq = collections.OrderedDict(sorted(location_freq.items(), key=lambda tup: tup[1], reverse=True))
	ordered_locations = location_freq.keys()
	
	
	#transform the dictionary into a 2 dimentional numpy array and select only the k-most frequent locations
	np_matrix = np.zeros((len(ordered_locations), 24))
	idex = 0
	for location in ordered_locations:
		np_matrix[idex,:]=location_count[location]
		idex+=1
		
			
	#create the distribution of locations by hour (normalizing each column)
	column_sums = np_matrix.sum(axis=0)
	location_dist = np_matrix[0:k,:] / column_sums[np.newaxis , :]
	ld_title = "top-"+str(k)+" distribution of locations by hour "+str(current_option)+" for user "+str(user_id)
	ld_x = "hours"
	ld_y = "Pr[location|hour]"
	
	
		
	#create the legends
	legends = [str(location)+", r="+str(location_metadata[DataExtractor.location_attribute][str(location)][DataExtractor.location_metaradius])+", c="+str(location_metadata[DataExtractor.location_attribute][str(location)][DataExtractor.location_metacenter]) for location in ordered_locations[0:k]]
	
	
	PlotlibDrawer.plot_np(None, location_dist, legends, ld_x, ld_y, ld_title, 0)
	
	#add an informative description in a log file containing the content of the clusters
	stream = LogsFileWriter.open("most_frequent_location_clusters_"+str(current_option)+"_user"+str(user_id))
	
	for location in ordered_locations[0:k]:
		LogsFileWriter.write("location "+str(location)+"\n"+JsonUtils.dict_as_json_str(location_metadata[DataExtractor.location_attribute][str(location)])+"\n\n\n", stream)
	
	LogsFileWriter.close(stream)
	
	

			
		
		
		
		
		
		
		
		
		
		

		
		
		
		