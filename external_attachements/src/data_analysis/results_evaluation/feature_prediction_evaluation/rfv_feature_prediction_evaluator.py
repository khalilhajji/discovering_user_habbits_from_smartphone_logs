#!/usr/bin/env python
import sys
from abc import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import Classifier
from clean_data_utils import *

import random as rnd
import numpy as np
import numpy.ma as ma
from abc import *
import collections
from feature_prediction_evaluator import FeaturePredictionEvaluator
import pdb

'''
This evaluation Method uses the Feature prediction metric: it evaluates how well a classifier is able to predict a hidden feature from the test data
1- the evaluated classifier is trained with a train set containing the feature to predict
2- the feature to predict is removed from the test set
3- the evaluated classifier tries to guess the value of the hidden feature from the test samples
'''
class RfvFeaturePredictionEvaluator(FeaturePredictionEvaluator):
	__metaclass__ = ABCMeta
	#rate of the training set with respect to the total dataset
	train_size = 0.8
	
	#in the name of the feature to predict
	feature_to_predict = None
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	class_names = None
	
	feature_not_present_id = -1
	unknown_class_id = -1
	def __init__(self, rfv_data, features, values, train_ids, test_ids):
		#the data_matrix
		self.rfv_data = rfv_data
		self.fnames = features
		self.vnames = values
		
		#get the ids of the features that we want to predict
		self.id_feature_to_predict = self.fnames.index(self.feature_to_predict)
		
		#list containing lists of value ids that are considered as the same class. First list corresponds to the ids of class 1, 2nd list of ids of class 2, ect...
		[self.classes, self.vc_dict] = self._def_classes()
		
		
		#filter the input matrix such that all the records it contain at least one realization for the ids to predict
		self.rfv_data = self._remove_records_not_containig_feature_to_predict()
		print "lenght cleaned rv_data"
		print len(self.rfv_data)
		
		#split the dataset into train and test set
		self.train_ids = train_ids; self.test_ids = test_ids
		if self.train_ids == None:
			[self.train_rfv, self.test_rfv, self.train_ids, self.test_ids] = self._build_train_test_dataset(RfvFeaturePredictionEvaluator.train_size)
		else:
			[self.train_rfv, self.test_rfv] = self._apply_train_test_split(self.train_ids, self.test_ids)
			
		#label each record in the test set with the corresponding class(es)
		self.test_labels = self._label_test_data()
		
		
		#regroup some records to label them as a group (if needed)
		v = self._group_records(self.test_labels)
		self.r_groups = None
		if v!= None:
			[self.r_groups, self.test_labels]=[v[0],v[1]]
		
		#hide the features to predict in the test set 
		self._hide_features_to_predict()
			
		
		
	
	'''
	This method evaluates the selected classifier and returns its accuracy on a test set
	returns [good_predictions, total_predictions, accuracy]
	'''
	def evaluate(self, classifier) :
		
		
		#train the classifier on the trainset
		classifier.train(self.train_rfv)
		
		#evaluate the classifier on the testset
		[predicted_classes, scores] = classifier.classify(self.test_rfv, self.id_feature_to_predict, self.r_groups, self.classes)
	
		#compute the accuracy of the classifier
		[good_predictions, total_predictions, accuracy] = self._compute_accuracy(predicted_classes, self.test_labels)
		accuracies = self._compute_macro_average_accuracy(predicted_classes, self.test_labels)
		
		#return [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
		return [good_predictions, total_predictions, accuracy]+accuracies
		
	
	def _remove_records_not_containig_feature_to_predict(self):
		filtered_rfv = {}
		fr = 0
		for r in self.rfv_data:
			if self.id_feature_to_predict in self.rfv_data[r]:
				filtered_rfv[fr]=self.rfv_data[r]
				fr += 1 
		
		
		return filtered_rfv
		
		
	def _build_train_test_dataset(self, train_size):
		train_rfv = {}; trids = []; trr = 0;
		test_rfv = {}; teids=[]; ter = 0;
		for r in self.rfv_data:
			rand = rnd.random()
			if rand <= train_size:
				train_rfv[trr]=self.rfv_data[r]
				trids.append(r)
				trr+=1
			else:
				test_rfv[ter]= self.rfv_data[r]
				teids.append(r)
				ter+=1
			
		return [train_rfv, test_rfv, trids, teids]
		
	def _apply_train_test_split(self, train_ids, test_ids):
		train_rfv = {}; trr = 0;
		test_rfv = {}; ter = 0;
		for r in train_ids:
			train_rfv[trr]=self.rfv_data[r]
			trr+=1
			
		for r in test_ids:
			test_rfv[ter]=self.rfv_data[r]
			ter+=1
		
		return [train_rfv, test_rfv]
		
		
	@abstractmethod
	def _def_classes(self):
		return None
	
	
	
	'''
	return [groups, labels] where groups is a list of list where each list represents the ids of the records regrouped together
								  labels is a list containing the class number of each group
			if return None then no group will be made and each group is considered separately
	'''
	@abstractmethod
	def _group_records(self, test_set_labels):
		return None
		
	
	def _label_test_data(self):
		labels = []
		for r in self.test_rfv:
			record_classes = list({self.vc_dict[v] for v in self.test_rfv[r][self.id_feature_to_predict]})
			labels.append(record_classes)
		return labels
		

	def _hide_features_to_predict(self):
		for r in self.test_rfv:
			del self.test_rfv[r][self.id_feature_to_predict]
		
		
'''
This class evaluates the classifiers in their capacity to predict well the Location feature when it is hidden
'''		
class RfvLocationPredictionEvaluator (RfvFeaturePredictionEvaluator):
	feature_to_predict = "location" #the name of the feature to predict
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	class_names = ["most_frequent", "second_most_frequent", "others"]
	
	def __init__(self, rfv_data, features, values, train_ids, test_ids):
		RfvFeaturePredictionEvaluator.__init__(self, rfv_data, features, values, train_ids, test_ids)
		
	
	def _def_classes(self):
		values = self.vnames[self.id_feature_to_predict]
		classes = [] #contains lists where each list represent a group of values that represent the same class. 1st list is values representing 1st class, ...
		vc_dict = {} # associates to each value its corresponding class
		
		#the locations are sorted by the most frequent to the least frequent location
		classes.append([0]) #value 0 represents the most_frequent class
		vc_dict[0]=0
		
		classes.append([1]) #value 1 represents the second_most_frequent class
		vc_dict[1]=1
		
		third_class = []
		for id, vname in enumerate(values[2:]): third_class.append(id+2); vc_dict[id+2]=2; #all the others represent the other class	
		classes.append(third_class)
		

		return [classes, vc_dict]
		
		
		
	def _group_records(self, test_set_labels):
		return None
		
		
'''
This class evaluates the classifiers in their capacity to predict well the day of a record when it is hidden
'''	
class RfvDayPredictionEvaluator (RfvFeaturePredictionEvaluator):
	feature_to_predict = "day" #the name of the feature to predict
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	class_names = ["week_day", "week_end"]
	
	def __init__(self, rfv_data, features, values, train_ids, test_ids):
		RfvFeaturePredictionEvaluator.__init__(self, rfv_data, features, values, train_ids, test_ids)
	
	
	def _def_classes(self):
		values = self.vnames[self.id_feature_to_predict]
		classes = [] #contains lists where each list represent a group of values that represent the same class. 1st list is values representing 1st class, ...
		vc_dict = {} # associates to each value its corresponding class
		
		#the values 5,6 corresponds to saturday, sunday (class 1). the others (from 0 to 4) to the week days(class 0). Thus in the ids, the two last ones correspond to the week_ends and the others to the week days
		first_class = []
		for i in range(5): first_class.append(i); vc_dict[i]=0
		classes.append(first_class)
		
		classes.append([5,6])
		vc_dict[5]=1
		vc_dict[6] = 1
		
		return [classes, vc_dict]
		
		
	'''
	we want to regroup the successive records that have the same class_id
	'''	
	def _group_records(self, test_set_labels):
		'''#we know that for the day feature, each record can belong to only one class. thus test_set_labels has the format [[class_nb],[class_nb],...]
		groups = []
		group_labels = []
		
		current_group = []
		id = 0
		for current_label_list in test_set_labels:
			current_label = current_label_list[0]
			if len(current_group) == 0:
				#it is a new empty group so add the id of the current label and save the label of the new created group
				current_group.append(id)
				group_labels.append([current_label])
			
			elif len(current_group)>0 and group_labels[-1][0] == current_label:
				#the current label is the same than the last one, so add the id to the current group
				current_group.append(id)
			elif len(current_group)>0 and group_labels[-1][0] != current_label:
				#the current label is different from the last one, so close the actual current group and create a new one
				groups.append(current_group)
				current_group = []
				current_group.append(id)
				group_labels.append([current_label])
			id += 1

			
		#add the last group
		groups.append(current_group)
				
			
			
		return [groups, group_labels]'''
		return None
		
		
class RfvApplaunchPredictionEvaluator (RfvFeaturePredictionEvaluator):
	feature_to_predict = "appLaunch" #the name of the feature to predict
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	class_names = ["1st_frequent", "2nd_frequent", "3rd_frequnet", "5th_frequent", "6th_frequent", "others"]
	
	def __init__(self, rfv_data, features, values, train_ids, test_ids):
		RfvFeaturePredictionEvaluator.__init__(self, rfv_data, features, values, train_ids, test_ids)
	
	
	def _def_classes(self):
		values = self.vnames[self.id_feature_to_predict]
		classes = [] #contains lists where each list represent a group of values that represent the same class. 1st list is values representing 1st class, ...
		vc_dict = {} # associates to each value its corresponding class
		
		for i in range(6):
			#the locations are sorted by the most frequent to the least frequent location
			classes.append([i]) #value 0 represents the most_frequent class
			vc_dict[i]=i
		
		
		
		seventh_class = []
		for id, vname in enumerate(values[6:]): seventh_class.append(id+6); vc_dict[id+6]=6; #all the others represent the other class	
		classes.append(seventh_class)
		
		return [classes, vc_dict]
		
		
	'''
	we want to regroup the successive records that have the same class_id
	'''	
	def _group_records(self, test_set_labels):
		return None
	
		
		
	
		
	