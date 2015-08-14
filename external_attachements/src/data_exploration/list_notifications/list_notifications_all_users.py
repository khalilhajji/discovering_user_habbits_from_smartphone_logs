'''
Script that outputs a file in the log directory containing the different notification types that occured in the dataset and their number
of occurrences (for all the users)
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import collections

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from list_notifications_one_user import list_notifications_one_user as lnou
from logs_file_writer import LogsFileWriter

stream = LogsFileWriter.open("notifications_list")
LogsFileWriter.write("different notifications types and their number of occurrences in the dataset \n\n", stream)

notifications_list = {}

for user_id in DataExtractor.users_ids_list():
	current_list= lnou(user_id)
	
	for key, value in current_list.iteritems():
		if key not in notifications_list:
			notifications_list[key]=collections.Counter()
		
		notifications_list[key] += value
	
	current_list = collections.OrderedDict(sorted(current_list.items(),key = lambda t: t[1]['records'], reverse=True))
	LogsFileWriter.write("\n\n user "+str(user_id)+" notification list : \n", stream)
	LogsFileWriter.write(str(json.dumps(current_list, indent=4)), stream)
	print("user "+str(user_id)+" extracted")
	
#sort the notifications by decreasing order	
notifications_list = collections.OrderedDict(sorted(notifications_list.items(),key = lambda t: t[1]['records'], reverse=True))


LogsFileWriter.write("\n\n all users notification list : \n", stream)
LogsFileWriter.write(str(json.dumps(notifications_list, indent=4)), stream)
LogsFileWriter.close(stream)