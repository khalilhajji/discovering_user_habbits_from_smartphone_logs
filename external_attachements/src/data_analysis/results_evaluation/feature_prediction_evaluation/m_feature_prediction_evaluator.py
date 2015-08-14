
#!/usr/bin/env python
import sys
from abc import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import Classifier
from clean_data_utils import *

from sklearn.cross_validation import train_test_split
import numpy as np
import numpy.ma as ma
from abc import *
import collections
from feature_prediction_evaluator import FeaturePredictionEvaluator
import random as rnd

'''
This evaluation Method uses the Feature prediction metric: it evaluates how well a classifier is able to predict a hidden feature from the test data
1- the evaluated classifier is trained with a train set containing the feature to predict
2- the feature to predict is removed from the test set
3- the evaluated classifier tries to guess the value of the hidden feature from the test samples
'''
class MFeaturePredictionEvaluator(FeaturePredictionEvaluator):
	__metaclass__ = ABCMeta
	#rate of the training set with respect to the total dataset
	train_size = 0.8
	
	#in the row labels, the prefix that corresponds to the target feature
	label_prefix = None
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	classes = None
	
	feature_not_present_id = -1
	unknown_class_id = -1
	def __init__(self, matrix, row_labels, columns_labels, train_ids, test_ids):
		#the data_matrix
		self.x_matrix = matrix
		self.row_labels = row_labels
		self.columns_labels = columns_labels
		
		#get the ids of the features that we want to predict
		self.ids_to_predict = self.get_ids_features_to_predict(self.row_labels, self.label_prefix)
		
		#keys are class names and values are the corresponding class numbers
		self.classes_dic = self.attribute_numbers_to_classes(self.classes)
		
		#to each feature id, maps a class number
		self.feature_class_translator = self.create_featureid_classnb_dict(self.ids_to_predict, self.classes_dic)
		#add the unknown class number (feature_id = -1 corresponds to class -1)
		self.feature_class_translator[MFeaturePredictionEvaluator.feature_not_present_id] = MFeaturePredictionEvaluator.unknown_class_id
		
		#filter the input matrix such that all the records it contain at least one realization for the ids to predict
		self.x_matrix = self._remove_records_not_containig_ids_to_predict(self.x_matrix, self.ids_to_predict, 1, 0)
		
		#split the dataset into train and test set
		self.train_ids = train_ids; self.test_ids = test_ids
		if self.train_ids == None:
			[self.x_train, self.x_test, self.train_ids, self.test_ids] = self.build_train_test_dataset(self.x_matrix, MFeaturePredictionEvaluator.train_size)
			
		else:
			[self.x_train, self.x_test] = [self.matrix[:,self.train_ids], self.matrix[:,self.test_ids]]
			
		
		
	
	'''
	This method evaluates the selected classifier and returns its accuracy on a test set
	returns [good_predictions, total_predictions, accuracy]
	'''
	def evaluate(self, classifier) :
		
		[x_train, x_test] = [self.x_train, self.x_test]
		
		#label each record in the test set with the corresponding class(es)
		test_labels = self.label_data(x_test, self.ids_to_predict, self.feature_class_translator, 1)
	
		
		#regroup some records to label them as a group (if needed)
		v = self.group_records(test_labels)
		groups = None
		if v!= None:
			[groups, test_labels]=[v[0],v[1]]
		
		#hide the features to predict in the test set 
		x_test = self.hide_features_to_predict(x_test, self.ids_to_predict, 1)
		
		#train the classifier on the trainset
		classifier.train(x_train)
		
		#evaluate the classifier on the testset
		[predicted_features, scores] = classifier.classify(x_test, self.ids_to_predict, groups)
	
		
		#transform the predicted features into classes numbers
		predicted_classes = self.from_featureid_to_classnb(predicted_features, self.feature_class_translator)
	
		#compute the accuracy of the classifier
		[good_predictions, total_predictions, accuracy] = self._compute_accuracy(predicted_classes, test_labels)
		accuracies = self._compute_macro_average_accuracy(predicted_classes, test_labels)
		
		#return [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
		return [good_predictions, total_predictions, accuracy]+accuracies
		
	
	def _remove_records_not_containig_ids_to_predict(self, matrix_data, ids_to_predict, record_dimention, feature_dimention):
		#transform the data such that the target features remain unchanged and all the others equal to 0
		mask = np.zeros(np.shape(matrix_data))
		if record_dimention == 0:
			mask[:, ids_to_predict ] = 1

		elif record_dimention == 1: 
			mask[ids_to_predict, :] = 1
		
		masked_data = matrix_data * mask
		
		#sum the entries of each record, if they are > than 0 we keep them
		sums = np.sum(masked_data, feature_dimention)
		
	
		
		if record_dimention == 0:
			filtered_data = matrix_data[np.nonzero(sums)[0], :]
		
		elif record_dimention == 1: 
			filtered_data = matrix_data[:, np.nonzero(sums)[0]]
		
		return filtered_data
		
		
	def build_train_test_dataset(self, matrix, tran_size):
		print matrix
		print np.size(matrix, 1)
		nb_records = np.size(matrix, 1)
		trids = []
		teids = []
	
		for r in range(nb_records): 
			if rnd.random() <= tran_size: trids.append(r);		
			else: teids.append(r)
			
		[x_train, x_test] = [matrix[:,trids], matrix[:,teids]]
		
		return [x_train, x_test, trids, teids]
	
	
	
	'''
	return [groups, labels] where groups is a list of list where each list represents the ids of the records regrouped together
								  labels is a list containing the class number of each group
			if return None then no group will be made and each group is considered separately
	'''
	@abstractmethod
	def group_records(self, test_set_labels):
		return None
		
		
	def get_ids_features_to_predict(self, ordered_labels, target_label_prefix):
		ids = []
		id = 0
		for label in ordered_labels:
			if label.startswith((target_label_prefix)):
				ids.append(id)
			
			id+=1
		
		return ids
		
	def attribute_numbers_to_classes(self, classes_names):
		s_class_names = sorted(classes_names)
		numbers_dict = {}
		
		id = 0
		for name in s_class_names:
			numbers_dict[name] = id
			id += 1
	
	@abstractmethod
	def create_featureid_classnb_dict(self, feature_ids, classes_dict):
		return None
		
	
	def label_data(self, matrix_data, ids_to_hide, feature_class_translator, record_dimention):
		#transform the data such that the target features remain unchanged and all the others equal to 0
		mask = np.zeros(np.shape(matrix_data))
		if record_dimention == 0:
			mask[:, ids_to_hide ] = 1

		elif record_dimention == 1: 
			mask[ids_to_hide, :] = 1
		
		masked_data = matrix_data * mask
		
		labels = []
		#for each record, get the indicies that equal to 1
		records_number = masked_data.shape[record_dimention]
		if record_dimention == 0:
			for id in range (0, records_number):
				record = masked_data[id,:]
				record_classes = self.get_classes_of_one_record(record, feature_class_translator)
				labels.append(record_classes)
				
		elif record_dimention == 1:
			for id in range (0, records_number):
				record = masked_data[:,id]
				record_classes = self.get_classes_of_one_record(record, feature_class_translator)
				labels.append(record_classes)
				
		else :
			raise Exception("INCORRECT ARGUMENT EXCEPTION: the dimention "+str(record_dimention)+" is incorrect")
			
			
		return labels
				
		
	def get_classes_of_one_record(self, record_vector, feature_class_translator):
		features_present = record_vector.nonzero()[0].tolist()
		
		if features_present == []:
			#All the features are equal to 0
			features_present.append(MFeaturePredictionEvaluator.feature_not_present_id)
		
		classes = list(set(self.from_featureid_to_classnb(features_present, feature_class_translator)))
		
		return classes
		
	'''
	hiding them means putting them to 0's
	'''	
	def hide_features_to_predict(self, matrix_data, ids_to_hide, record_dimention):
		mask = np.ones(np.shape(matrix_data))
		

		
		if record_dimention == 0:
			mask[:, ids_to_hide ] = 0

		elif record_dimention == 1: 
			mask[ids_to_hide, :] = 0
					
		else :
			raise Exception("INCORRECT ARGUMENT EXCEPTION: the dimention "+str(record_dimention)+" is incorrect")	
		ma_matrix = matrix_data* mask
		
	
		return ma_matrix
	'''
	from a list of feature ids returns a list of the same size of corresponding class nbs where
	'''
	def from_featureid_to_classnb(self, featureid_list, feature_class_translator):
		classes = [feature_class_translator[feature] for feature in featureid_list]
		return classes
		
		
'''
This class evaluates the classifiers in their capacity to predict well the Location feature when it is hidden
'''		
class MLocationPredictionEvaluator (MFeaturePredictionEvaluator):
	#in the row labels, the prefix that corresponds to the target feature
	label_prefix = "location__place__"
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	classes = ["most_frequent", "second_most_frequent", "others"]
	
	def __init__(self, matrix, row_labels, columns_labels, train_ids, test_ids):
		MFeaturePredictionEvaluator.__init__(self, matrix, row_labels, columns_labels, train_ids, test_ids)
		
		
	def create_featureid_classnb_dict(self, feature_ids, classes_dict):
		#the ids of the location are sorted by the most frequent to the least frequent location
		sorted_ids = sorted(feature_ids)
		featureid_classnb_dict = {}
		#smallest_id corresponds to class 0
		featureid_classnb_dict[sorted_ids[0]]=0 
		
		#second_smallest_id corresponds to class 1
		featureid_classnb_dict[sorted_ids[1]]=1
		
		#the others to class 2
		for i in range(2, len(sorted_ids)):
			featureid_classnb_dict[sorted_ids[i]]=2
			
		return featureid_classnb_dict
		
		
		
	def group_records(self, test_set_labels):
		return None
		
		
'''
This class evaluates the classifiers in their capacity to predict well the day of a record when it is hidden
'''	
class MDayPredictionEvaluator (MFeaturePredictionEvaluator):
	#in the row labels, the prefix that corresponds to the target feature
	label_prefix = "time_day_"
	
	#list containing the class names that we want to classify our hidden feature in ex: [weed_end, week_days] 
	classes = ["week_day", "week_end"]
	
	def __init__(self, matrix, row_labels, columns_labels, train_ids, test_ids):
		MFeaturePredictionEvaluator.__init__(self, matrix, row_labels, columns_labels, train_ids, test_ids)
		
		
	def create_featureid_classnb_dict(self, feature_ids, classes_dict):
		#the values 5,6 corresponds to saturday, sunday (class 1). the others (from 0 to 4) to the week days(class 0). Thus in the ids, the two last ones correspond to the week_ends and the others to the week days
		reverse_sorted_ids = sorted(feature_ids, reverse = True)
		featureid_classnb_dict = {}
		#smallest_id corresponds to class 0
		featureid_classnb_dict[reverse_sorted_ids[0]]=1 
		
		#second_smallest_id corresponds to class 1
		featureid_classnb_dict[reverse_sorted_ids[1]]=1
		
		#the others to class 2
		for i in range(2, len(reverse_sorted_ids)):
			featureid_classnb_dict[reverse_sorted_ids[i]]=0
			
		return featureid_classnb_dict
		
		
	'''
	we want to regroup the successive records that have the same class_id
	'''	
	def group_records(self, test_set_labels):
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
	
		
		
	
		
	