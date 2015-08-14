#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from evaluation_perplexity_one_user import evaluation_perplexity_one_user as epou
from logs_file_writer import LogsFileWriter
from matrix_data_utils import *



file_name = "evaluation_perplexity"
#contains the scores of the different predictors combined for all the users
mixed_evaluations = {}

#contains the scores details of the different predictors for each user 
detailed_evaluations = {}
iter = 0
for user_id in MDataExtractor.users_ids_list():
	print("user "+str(user_id)+" on working")
	evaluations = epou(user_id)
		
	if len(detailed_evaluations.keys()) == 0:
		#instantiate the evaluations objects add the classifier names for detailed_evaluations and detailed_evaluations
		for classifier_name, evaluation_results in evaluations.iteritems():
			mixed_evaluations[classifier_name] = {"average perplexity":0}
			detailed_evaluations[classifier_name] = {}
				
	#integrate the evaluations of the current users
	for classifier_name, perplexity in evaluations.iteritems():
		mixed_evaluations[classifier_name]["average perplexity"] = ((mixed_evaluations[classifier_name]["average perplexity"]*iter)+perplexity)/((iter+1)*1.0)
			
		#update the detailed evaluations
		detailed_evaluations[classifier_name]["user "+str(user_id)]= {"perplexity": perplexity}
		
	iter+=1
	print("user "+str(user_id)+" extracted")
			
#write the dictionaries into files
out = LogsFileWriter.open(file_name)
LogsFileWriter.write("perplexity \n",out)
LogsFileWriter.write("Total scores :\n",out)
LogsFileWriter.write(JsonUtils.dict_as_json_str(mixed_evaluations),out)
LogsFileWriter.write("detailed scores :\n",out)
LogsFileWriter.write(JsonUtils.dict_as_json_str(detailed_evaluations),out)
LogsFileWriter.close(out)
