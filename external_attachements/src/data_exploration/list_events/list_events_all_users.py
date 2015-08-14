'''
Script that outputs a file in the log directory containing the different events types that occured in the dataset and their number
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
from list_events_one_user import list_events_one_user as leou
from logs_file_writer import LogsFileWriter

stream = LogsFileWriter.open("events_list")
LogsFileWriter.write("different events types and their number of occurrences in the dataset \n\n", stream)

events_list = collections.Counter()

for user_id in DataExtractor.users_ids_list():
	current_list = collections.Counter(leou(user_id))
	events_list += current_list
	
	LogsFileWriter.write("\n\n user "+str(user_id)+" event list : \n", stream)
	LogsFileWriter.write(str(json.dumps(current_list, indent=4)), stream)
	print("user "+str(user_id)+" extracted")
	
#sort the notifications by decreasing order	
events_list = collections.OrderedDict(sorted(events_list.items(),key = lambda t: t[1], reverse=True))


LogsFileWriter.write("\n\n all users notification list : \n", stream)
LogsFileWriter.write(str(json.dumps(events_list, indent=4)), stream)
LogsFileWriter.close(stream)