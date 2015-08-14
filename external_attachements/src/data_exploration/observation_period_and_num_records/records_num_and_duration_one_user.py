'''
see how many records does it have and how long is the period of this observation for one given user(the id of 
the user is given as argument)
'''
#!/usr/bin/env python
import sys
import json
import os
import datetime
from pprint import *

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import DataExtractor

def records_num_and_duration_one_user(user_id):
	
	data = DataExtractor.load_json_data(user_id)
	
	
	records_number = len(data)
	first_record_date = datetime.date(2020,1,1)
	last_record_date = datetime.date(1970,1,1)
	for record_id in data:
		current_date = DataExtractor.date_of_record(data[record_id])
		
		
		if current_date > last_record_date:
			last_record_date = current_date
		if current_date<first_record_date:
			first_record_date=current_date
		
	
	
	records_duration = last_record_date - first_record_date
	
	first_record_date_str = first_record_date.strftime('%Y-%m-%d')
	last_record_date_str = last_record_date.strftime('%Y-%m-%d')
	
	average_records_per_day = records_number*1.0/int(records_duration.days)
	
	
	str_res = ('number of records: '+str(records_number)+' \nfirst record date: '+first_record_date_str+
	'\nlast_record_date: '+last_record_date_str+'\nobservation period: '+str(records_duration.days)+
	' days\naverage records per day:'+str(average_records_per_day)+'\n')
	
	
	return str_res