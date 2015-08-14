'''
function that computes the different notification types that occured for a specified user and their number
of occurrences.

returns a dictionary where the keys are the notification package name and the values the number of occurrences
of that notification for the specified user. The dictionary is ordered so that the most frequent notifications 
come at first and the less frequents at the end.
'''
#!/usr/bin/env python
import sys
import datetime
from pprint import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *

def list_notifications_one_user(user_id):
	data = DataExtractor.load_json_data(user_id)
	return DataOperations.get_notification_names_count_and_priority(data)