'''
for each feature, test how much this feature is present in each record for each user. For each feature,
outputs a percentage  between 0 and 100. 100% means that the feature is present in 100% 
of the records, 0% means that is present in 0% of the records. 
The result is written in a file in the logs directory.
'''

#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from features_presence_rate_one_user import features_presence_rate_one_user
from logs_file_writer import LogsFileWriter


json_data_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/"


#array containing the path to the validated json fata for each user
users_json_files_array = [json_data_dir+x+"/all/all_in_one_validated_log.json" for x in os.listdir(json_data_dir)]

pp.pprint(users_json_files_array)
features_presence_rate =''
user_number = 1
for json_file in users_json_files_array:
	if os.path.isfile(json_file):
		features_presence_rate = features_presence_rate + "\n \n \n user "+str(user_number)+"\n"+ features_presence_rate_one_user(json_file)
	print("user "+str(user_number)+" extracted")
	user_number+=1

#write the results to the log file
stream = LogsFileWriter.open("features_presence_rate")
LogsFileWriter.write(features_presence_rate, stream)
LogsFileWriter.close(stream)