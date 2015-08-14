'''
function that computes the different event types that occured for a specified user and their number
of occurrences.

Outputs a dictionary where the keys are the event type and the values the number of occurrences
of that notification for the specified user. The dictionary is ordered so that the most frequent events 
come at first and the less frequents at the end.
'''
#!/usr/bin/env python
import sys
import datetime
from pprint import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *

def list_events_one_user(user_id):
	data = DataExtractor.load_json_data(user_id)
	return DataOperations.get_event_types_count(data)