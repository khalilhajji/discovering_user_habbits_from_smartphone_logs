'''
outputs the number of realizations(events) for each feature for all users
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from nb_realizations_by_feature_one_user import nb_realizations_by_feature_one_user as nrbfou
from logs_file_writer import LogsFileWriter
from clean_data_utils import DataExtractor


features_presence_rate =''
for user_id in DataExtractor.users_ids_list():
	features_presence_rate = features_presence_rate + nrbfou(user_id)
	print("user "+str(user_id)+" extracted")


#write the results to the log file
stream = LogsFileWriter.open("features_presence_rate")
LogsFileWriter.write(features_presence_rate, stream)
LogsFileWriter.close(stream)