#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from evaluation_on_location_prediction_one_user import evaluation_on_location_prediction_one_user as eolpou
from evaluation_on_day_prediction_one_user import evaluation_on_day_prediction_one_user as eodpou
from logs_file_writer import LogsFileWriter
from matrix_data_utils import *
from evaluation_on_applaunch_prediction_one_user import evaluation_on_applaunch_prediction_one_user as eoapou


def evaluation_on_feature_prediction_all_users(feature_name):
	#contains the scores of the different predictors combined for all the users
	mixed_evaluations = {}

	#contains the scores details of the different predictors for each user 
	detailed_evaluations = {}
	iter = 0
	for user_id in MDataExtractor.users_ids_list():
		print("user "+str(user_id)+" on working")
		if feature_name == "day":
			[evaluations,classes] = eodpou(user_id)
			file_name = "evaluation_day_prediction"
		elif feature_name == "location":
			[evaluations,classes] = eolpou(user_id)
			file_name = "evaluation_location_prediction"
		elif feature_name == "applaunch":
			[evaluations,classes] = eoapou(user_id)
			file_name = "evaluation_applaunch_prediction"
		else:
			raise Exception("NOT IMPLEMENTED FEATURE EXCEPTION: the feature "+str(feature_name)+" do not implemented or do not exist")
		
		if len(detailed_evaluations.keys()) == 0:
			#instantiate the evaluations objects add the classifier names for detailed_evaluations and detailed_evaluations
			for classifier_name, evaluation_results in evaluations.iteritems():
				mixed_evaluations[classifier_name] = {"correct predictions":0 , "total predictions":0, "accuracy":0, "average accuracy":0, "average macro_accuracy":0}
				detailed_evaluations[classifier_name] = {}
				
		#integrate the evaluations of the current users
		for classifier_name, evaluation_results in evaluations.iteritems():
			#evaluation_results = [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
			#update the mixed evaluations
			mixed_evaluations[classifier_name]["correct predictions"]+=evaluation_results[0]
			mixed_evaluations[classifier_name]["total predictions"]+=evaluation_results[1]
			mixed_evaluations[classifier_name]["accuracy"]= (mixed_evaluations[classifier_name]["correct predictions"]*1.0)/mixed_evaluations[classifier_name]["total predictions"]
			mixed_evaluations[classifier_name]["average accuracy"] = ((mixed_evaluations[classifier_name]["average accuracy"]*iter)+evaluation_results[2])/((iter+1)*1.0)
			mixed_evaluations[classifier_name]["average macro_accuracy"] = ((mixed_evaluations[classifier_name]["average macro_accuracy"]*iter)+evaluation_results[3])/((iter+1)*1.0)
			
			#update the detailed evaluations
			detailed_evaluations[classifier_name]["user "+str(user_id)]= {"correct predictions": evaluation_results[0], "total predictions":evaluation_results[1], "accuracy":evaluation_results[2], 
												"macro_accuracy":evaluation_results[3], "accuracy by class": evaluation_results[4:]}
		
		iter+=1
		print("user "+str(user_id)+" extracted")
		
		
		
	#write the results in a log file
	
	#write the dictionaries into files
	out = LogsFileWriter.open(file_name)
	LogsFileWriter.write("predictions on the classes "+JsonUtils.dict_as_json_str(classes)+"\n",out)
	LogsFileWriter.write("Total scores :\n",out)
	LogsFileWriter.write(JsonUtils.dict_as_json_str(mixed_evaluations),out)
	LogsFileWriter.write("detailed scores :\n",out)
	LogsFileWriter.write(JsonUtils.dict_as_json_str(detailed_evaluations),out)
	LogsFileWriter.close(out)
