'''
Outputs one plot per user, representing the number of record by day for each user.
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from records_by_day_one_user import records_by_day_one_user
from plot_lib_utils import PlotlibDrawer

json_data_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/"


#array containing the path to the validated json fata for each user
users_json_files_array = [json_data_dir+x+"/all/all_in_one_validated_log.json" for x in os.listdir(json_data_dir)]

pp.pprint(users_json_files_array)

user_number = 1

#for each user the metho records_by_day_one_user draws the plot
for json_file in users_json_files_array:
	if os.path.isfile(json_file):
		'''
		os.listdir(json_data_dir)[user_number-1] get the absolute name of the directory of the user which corresponds to 
		its id
		'''
		dict = records_by_day_one_user(json_file, str(user_number)+"("+(os.listdir(json_data_dir)[user_number-1])+")")
	print("user "+str(user_number)+" extracted")
	user_number+=1

PlotlibDrawer.show()
