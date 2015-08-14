'''
construct a plot representing the number of records by day of one user (the path to the json data
of that user is given in parameter.). To see the  graph, the method .show of the drawer needs to
be called (see utils dir).
another input is the user name so that it can be appended to the title of the plot.
produces at output a dictionary where the keys are the sorted string representation of dates (increasing order)
and where values are the number of records.
'''
#!/usr/bin/env python
import sys
import json
import datetime
import collections
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from plot_lib_utils import PlotlibDrawer

def records_by_day_one_user(file_name, user_name):
	json_data=open(file_name).read()
	data = json.loads(json_data)
	
	records_by_day={}
	previous_date= None
	previous_date_str=""
	for record in data['logInfo']:
		'''get the time of the first feature of any record. Note that the times of the different
		note that the time of the different features of the same record are close so we decided arbitrarily 
		to take the time of the first one'''
		try:
			current_time = data['logInfo'][record].iteritems().next()[1][u'createDate']
		except TypeError:
			#in some cases the first feature is an array of features
			current_time = data['logInfo'][record].iteritems().next()[1][0][u'createDate']
		
		current_date = datetime.datetime.fromtimestamp((current_time/1000.0))
		current_date_str = current_date.strftime('%Y-%m-%d')
		
		#add all the missing days between two records
		while previous_date_str != current_date_str and previous_date != None:
			if previous_date_str not in records_by_day:
				records_by_day[previous_date_str]=0
			
			if previous_date < current_date:
				previous_date += datetime.timedelta(days=1)
				previous_date_str = previous_date.strftime('%Y-%m-%d')
			elif previous_date > current_date:
				previous_date -= datetime.timedelta(days=1)
				previous_date_str = previous_date.strftime('%Y-%m-%d')
		
		#increase the counter of the corresponding record date by 1 record
		if current_date_str not in records_by_day:
			records_by_day[current_date_str]=0
		records_by_day[current_date_str]+=1
		
		previous_date = current_date
		previous_date_str = current_date_str
	
	
	#sort the dictionary by increasing dates
	ordered_dict_by_date = collections.OrderedDict(sorted(records_by_day.items()))
	
	
	#One label per 2 weeks
	nb_labels = len(ordered_dict_by_date.keys())/15
	PlotlibDrawer.plot(ordered_dict_by_date.keys(), ordered_dict_by_date.values(), "days", "records number", "records per day for user "+user_name, nb_labels)
	
	
	return ordered_dict_by_date