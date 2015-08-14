#!/usr/bin/env python
import sys
import json
import os
import datetime
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from clean_data_utils import *
from date_time_utils import *

'''
USED FOR CLEAN DATA : computes the amount of time we have information about the location of the user. In minutes.
'''
def location_time_coverage_one_user_clean(user_id):
	complete_data = DataExtractor.load_json_data(user_id)
	location_data = complete_data["location"]
	
	#the total number of minutes where we know the location of the user in the initial clean version of the data
	t_coverage_cln = 0
	
	
	
	iter = 0
	
	#this is to guarantee that we do not mark the same date more than ones (because it may occur that different realizations be mapped to the same hour)
	for date, location_feature in location_data.iteritems():
		#print "iteration "+str(iter)+" from "+str(len(location_data))
		iter+=1
		

		start_date = DataExtractor.start_date_of_realization_in_millis(date)
		end_date = DataExtractor.end_date_of_realization_in_millis(date)
		#get a list of datetimes representing the each hour covered between start date and end date
		t_coverage_cln += (float(end_date)-float(start_date))
		
	
	return t_coverage_cln/(1000*60)
		
	
	
	
	

			
		
		
		
		
		
		
		
		
		
		

		
		
		
		