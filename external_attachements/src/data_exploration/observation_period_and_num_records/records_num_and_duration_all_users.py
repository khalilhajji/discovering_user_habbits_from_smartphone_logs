'''
for each user, see how many records does it have and how long is the period of this observation
'''

#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from records_num_and_duration_one_user import records_num_and_duration_one_user as rnadou
from logs_file_writer import LogsFileWriter
from data_utils import DataExtractor


#rmadau stands for records num and duration all users
rmadau =''
user_number = 1
for user_id in DataExtractor.users_ids_list():
	rmadau = rmadau + "\n \n \n user "+str(user_id)+"("+str(DataExtractor.user_long_ids[user_id])+")\n"+ rnadou(user_id)
	print("user "+str(user_id)+" extracted")
	
#write the results to the log file
stream = LogsFileWriter.open("records_number_and_duration")
LogsFileWriter.write(rmadau, stream)
LogsFileWriter.close(stream)