'''
	in the original dataset we noticed a lot of noise and replication coming from the notification feature.
	the original data is in /speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/

	In this folder we face this problem by taking the original dataset and filtering the notifications without changing or modifying the structure
	of the data.
	
	for each of the users it does the filtering operation

	The filtering is done based on the following criterion:
	- some notifications is simply blacklisted because they correspond to some internal sony apps and thus not relevant for us
	- the notifications with a low priority is removed because they are not seen by the user
	- some redundant notifications will be collapsed into one. redundant notifications means the successive records that have the same notifications 
	that is just repeated in an interval of less than 5 seconds
	
	in the event feature, the event duplicated_notification is added to signal that a record has been generated due to a duplicate notification
	
	writes the filtered json data in json_data_dir = "/speech/dbwork/mul/students/dehajjik/notifications_filtered/"

	'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import collections

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from filter_notifications_one_user import filter_notifications_one_user as fnou

for user_id in DataExtractor.users_ids_list():
	data = fnou(user_id)
	print("user "+str(user_id)+" extracted")