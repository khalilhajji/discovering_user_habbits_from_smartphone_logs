'''
Class that represents the features co-occurrences for one user.
The path to the json data of the target user is specified in the constructor at the instantiation.
Then, 2 matrices are computed:
	- cooccurences_number: each cell (i,j) represents the number of co-occurrences 
	that feature i(row) and j(column) has. This matrix is thus diagonal.
	- cooccurences_rates: each cell (i,j) represents the percentage over the number of appearence
	of feature i in which i and j appeared together. This is the number of co-occurrences of feature 
	i and j divided by the number of occurrences of feature i.
	
There is a shared class array named features that indexes the ids of the different features. Thus the 
id=0 correspond to the first element in features (activityRecognitionResult_activity), ect...
'''

#!/usr/bin/env python
import sys
import os
import time
import json
import numpy as np

class UserFeaturesCooccurences():
	features = ['activityRecognitionResult_activity',
	'androidActivityRecognitionResult_activity',
	'appLaunch',
	'battery_health',
	'bluetooth',
	'notifications',
	'headsetPlug',
	'location',
	'networkInfo_state',
	'telephony',
	'wifiAps',
	'wifiConnectedAp'
	]
	def __init__(self, user_json_path):
		self.user_json_path = user_json_path
		#the number of times where two features appeared together
		self.cooccurences_number= np.zeros((len(UserFeaturesCooccurences.features),len(UserFeaturesCooccurences.features)))
		
		'''the percentage of which the feature in row appeared with the feature in the column. 
		How many times the feature in the row appeared with the feature in the column normalized 
		by the number of appearance of the row feature'''
		self.cooccurences_rates = np.zeros((len(UserFeaturesCooccurences.features),len(UserFeaturesCooccurences.features)))
		
		self.occurences_number = np.zeros((len(UserFeaturesCooccurences.features),len(UserFeaturesCooccurences.features)))
		
		json_data=open(self.user_json_path).read()
		data = json.loads(json_data)
		
		for record in data['logInfo']:
			for key_1, value_1 in data['logInfo'][record].iteritems():
				id_1 = self.get_key_id(key_1, value_1)
				if id_1 != -1 :
					self.occurences_number[id_1, :] += np.ones(len(UserFeaturesCooccurences.features))
					for key_2, value_2 in data['logInfo'][record].iteritems():
						id_2 = self.get_key_id(key_2, value_2)
						if id_2!=-1:
							self.cooccurences_number[id_1,id_2] +=1
		
		self.cooccurences_rates = np.nan_to_num((self.cooccurences_number*100).__div__(self.occurences_number))
					
					
	def get_key_id(self, key, value):
		if key == 'activityRecognitionResult' and value['activity'] != 'Unrecognizable motion':
			return UserFeaturesCooccurences.features.index('activityRecognitionResult_activity')
		elif key == 'androidActivityRecognitionResult' and value['activity'] != 'unknown':
			return UserFeaturesCooccurences.features.index('androidActivityRecognitionResult_activity')
		elif key == 'battery' and value['health'] != 1 and value['health'] != 'Battery health is unknown':
			return UserFeaturesCooccurences.features.index('battery_health')
		elif key == 'networkInfo' and value['state'] != 'UNKNOWN':
			return UserFeaturesCooccurences.features.index('networkInfo_state')
		elif key in UserFeaturesCooccurences.features:
			return UserFeaturesCooccurences.features.index(key)
		else:
			return -1