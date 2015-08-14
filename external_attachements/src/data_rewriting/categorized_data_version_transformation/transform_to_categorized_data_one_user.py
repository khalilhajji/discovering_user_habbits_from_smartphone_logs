#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_rewriting/categorized_data_version_transformation/transformers")
from json_utils import JsonUtils
from clean_data_utils import DataExtractor
#from tansformers.feature_transformer import *
from feature_transformer import *
from location_transformer import *
from notification_transformer import *
from applaunch_transformer import *
from battery_transformer import *
from headset_transformer import *
from bluetooth_transformer import *
from activity_transformer import *
'''
Takes the clean data version and transform it to categorized data. This Step may take some time (especially for extracting the locations)
make the categorized data transformation for one user
'''
def transform_to_categorized_data_one_user(user_id):
	out_path_prefix = "/speech/dbwork/mul/students/dehajjik/categorized_data/"
	data_key = "data"
	metadata_key = "metadata"
	
	print "loading data for user "+str(user_id)
	nontransformed_data = DataExtractor.load_json_data(user_id)
	#nontransformed_data = JsonUtils.load_json_data("/home/dehajjik/workspace/resources/sample_data_for_location_categorization_test.json")
	
	
	#the transfomers responsible for the features of the data categorization
	feature_transformers = {LocationTransformer.transformed_feature_name: LocationTransformer(nontransformed_data),
							NotificationTransformer.transformed_feature_name : NotificationTransformer(nontransformed_data),
							ApplaunchTransformer.transformed_feature_name : ApplaunchTransformer(nontransformed_data),
							BatteryTransformer.transformed_feature_name: BatteryTransformer(nontransformed_data),
							HeadsetTransformer.transformed_feature_name: HeadsetTransformer(nontransformed_data),
							BluetoothPairedTransformer.transformed_feature_name: BluetoothPairedTransformer(nontransformed_data),
							BluetoothSeenTransformer.transformed_feature_name: BluetoothSeenTransformer(nontransformed_data),
							ActivityTransformer.transformed_feature_name : ActivityTransformer(nontransformed_data)}
	
	#the features that we want to transform
	selected_features = [LocationTransformer.transformed_feature_name,
						NotificationTransformer.transformed_feature_name,
						ApplaunchTransformer.transformed_feature_name,
						#BatteryTransformer.transformed_feature_name,
						#HeadsetTransformer.transformed_feature_name,
						BluetoothPairedTransformer.transformed_feature_name,
						#BluetoothSeenTransformer.transformed_feature_name,
						ActivityTransformer.transformed_feature_name]
						
	#selected_features = [ActivityTransformer.transformed_feature_name]
	
	
	categorized_data = {}
	categorized_data[data_key]={}
	categorized_data[metadata_key]={}
	
	
	for feature in selected_features:
		feature_transformers[feature].transform()
		if feature_transformers[feature].transformed_feature_data != {None:None} and feature_transformers[feature].transformed_feature_metadata != {None:None}:
			categorized_data[data_key][feature]= feature_transformers[feature].transformed_feature_data
			categorized_data[metadata_key][feature] = feature_transformers[feature].transformed_feature_metadata
	
	JsonUtils.save_json_data(out_path_prefix+str(DataExtractor.user_long_ids[user_id])+"/all/all_in_one_validated_log", categorized_data)
	return categorized_data