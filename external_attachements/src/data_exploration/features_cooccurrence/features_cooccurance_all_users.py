'''
for each user, computes the features co-occurrences.
Then, computes the overall co-occurrences (for all users)
For each entry, 2 matrices are computed:
	- cooccurences_number: each cell (i,j) represents the number of co-occurrences 
	that feature i(row) and j(column) has. This matrix is thus diagonal.
	- cooccurences_rates: each cell (i,j) represents the percentage over the number of appearence
	of feature i in which i and j appeared together. This is the number of co-occurrences of feature 
	i and j divided by the number of occurrences of feature i.
	
The name,id correspondence of the different features is given at the beginning. The 
id=0 corresponds for example to the first element in features (activityRecognitionResult_activity), ect..
'''
#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from features_cooccurance_one_user import UserFeaturesCooccurences
from logs_file_writer import LogsFileWriter
import numpy as np
from numpy_utils import Numpy as n

json_data_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/"


#array containing the path to the validated json fata for each user
users_json_files_array = [json_data_dir+x+"/all/all_in_one_validated_log.json" for x in os.listdir(json_data_dir)]

pp.pprint(users_json_files_array)
total_features_cooccurences_number = np.zeros((len(UserFeaturesCooccurences.features),len(UserFeaturesCooccurences.features)))
total_features_occurences_number = np.zeros((len(UserFeaturesCooccurences.features),len(UserFeaturesCooccurences.features)))
result = "\n\n\nThe features ids follows the order below : \n"+pp.pformat(UserFeaturesCooccurences.features)
user_number = 1
for json_file in users_json_files_array:
	if os.path.isfile(json_file):
		ufc = UserFeaturesCooccurences(json_file)
		total_features_cooccurences_number = total_features_cooccurences_number.__add__(ufc.cooccurences_number)
		total_features_occurences_number = total_features_occurences_number.__add__(ufc.occurences_number)
		result = (result+"\n \n \n user "+str(user_number)+"\n"+ "co-occurrences number matrix:\n"+
		n.str(ufc.cooccurences_number)+"\n\nco-occurrences rate matrix:\n"+n.str(ufc.cooccurences_rates))
	print("user "+str(user_number)+" extracted")
	user_number+=1

#compute the overall rate and add it to the result
total_features_cooccurences_rate = np.nan_to_num((total_features_cooccurences_number*100).__div__(total_features_occurences_number))
result = (result + "\n \n \n overall users\n"+ "co-occurrences number matrix:\n"+
		n.str(total_features_cooccurences_number)+"\n\nco-occurrences rate matrix:\n"+
		n.str(total_features_cooccurences_rate))

#write an explanation about the results
comment = ("This file represents the co-occurrences of the different features. \n"+  
"For each user, 2 matrices are shown:\n"+ 
	"- cooccurences_number: each cell (i,j) represents the number of co-occurrences \n"+ 
	"that feature i(row) and j(column) has. This matrix is thus diagonal.\n"+ 
	"- cooccurences_rates: each cell (i,j) represents the percentage over the number of appearence\n"+ 
	"of feature i in which i and j appeared together. This is the number of co-occurrences of feature \n"+ 
	"i and j divided by the number of occurrences of feature i.\n"+ 
"finally the overall users results are shown \n"+	
"The name,id correspondence of the different features is given at the beginning. The \n"+ 
"id=0 corresponds for example to the first element in features (activityRecognitionResult_activity), ect..."	)	

#write the results to the log file
stream = LogsFileWriter.open("features_cooccurrence")
LogsFileWriter.write(comment, stream)
LogsFileWriter.write(result, stream)
LogsFileWriter.close(stream)