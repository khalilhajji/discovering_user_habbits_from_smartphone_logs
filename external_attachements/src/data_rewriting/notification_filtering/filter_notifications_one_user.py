'''
	in the original dataset we noticed a lot of noise and replication coming from the notification feature.
	the original data is in /speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/

	In this folder we face this problem by taking the original dataset and filtering the notifications without changing or modifying the structure
	of the data.
	
	takes as input the id of the user and writes it's filtered data

	The filtering is done based on the following criterion:
	- some notifications is simply blacklisted because they correspond to some internal sony apps and thus not relevant for us
	- the notifications with a low priority is removed because they are not seen by the user
	- some redundant notifications will be collapsed into one. redundant notifications means the successive records that have the same notifications 
	that is just repeated in an interval of less than 5 seconds
	
	in the event feature, the event duplicated_notification is added to signal that a record has been generated due to a duplicate notification
	
	writes the filtered json data in json_data_dir = "/speech/dbwork/mul/students/dehajjik/notifications_filtered/"

	'''
from pprint import *
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from json_utils import JsonUtils

def filter_notifications_one_user(user_id):	
	out_path_prefix = "/speech/dbwork/mul/students/dehajjik/notifications_filtered/"
	data = DataExtractor.load_json_data(user_id)
	data = DataOperations.filter_notifications(data)
	
	JsonUtils.save_json_data(out_path_prefix+str(DataExtractor.user_long_ids[user_id])+"/all/all_in_one_validated_log", data)
	return data