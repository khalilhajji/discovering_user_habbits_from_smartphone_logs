#!/usr/bin/env python
import sys
import pprint as pp
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
import numpy as np
import numpy.ma as ma
from abc import *
import random




'''
is an abstract class that represents a classifier. It provides methods as train and classify
'''
class Classifier (object):

	__metaclass__ = ABCMeta
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	@abstractmethod
	def train(self, data):
		return None
	

#-------------------------M CLASSIFIER-------------------------------------------			
class MClassifier (Classifier):

	__metaclass__ = ABCMeta
	
	unknown_feature_id = -1
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	@abstractmethod
	def train(self, train_data_matrix):
		return None
	

	'''
	classify the test set elements
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	@abstractmethod
	def classify_with_no_regroup(self, test_data_matrix, ids_features_to_classify):
		return None
	
	
	'''
	classify the test set elements and then regroup the classified elements according to their group to decide a common class for them
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	groups: [[id1_groupe1,...,id_n1_groupe1],...,[id_1_groupem, ..., id_nm_groupem]]
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list that contains the scores corresponding to the decided features
	'''
	@abstractmethod	
	def regroup_and_classify(self, test_data_matrix, ids_features_to_classify, groups):
		return None
		
		
	def classify (self, test_data_matrix, ids_features_to_classify, groups):
		if groups == None:
			return self.classify_with_no_regroup(test_data_matrix, ids_features_to_classify)
			
		else:
			return self.regroup_and_classify(test_data_matrix, ids_features_to_classify, groups)
			
#-------------------------RV CLASSIFIER-------------------------------------------
class RVClassifier (Classifier):

	__metaclass__ = ABCMeta
	
	
	def __init__(self, vocab_size):
		self.vocab_size = vocab_size
		
	
	'''
	train the classifier on the given train data in the rfv format
	'''
	@abstractmethod
	def train(self, train_data_rv):
		return None
	

	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	id_feature_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	@abstractmethod
	def classify_with_no_regroup(self, test_data_rv, ids_realizations_to_classify,v_groups):
		return None
	
	
	'''
	classify the test set elements and then regroup the classified elements according to their group to decide a common class for them
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	r_groups: [[id1_groupe1,...,id_n1_groupe1],...,[id_1_groupem, ..., id_nm_groupem]] group of records that get a common classification
	v_groups: list containing the list of values that should be considered as unique classification class
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list that contains the scores corresponding to the decided features
	'''
	@abstractmethod	
	def regroup_and_classify(self, test_data_rfv, ids_realizations_to_classify, r_groups, v_groups):
		return None
		
		
	def classify (self, test_data_rfv, ids_realizations_to_classify, r_groups, v_groups):
		if r_groups == None:
			return self.classify_with_no_regroup(test_data_rfv, ids_realizations_to_classify, v_groups)
			
		else:
			return self.regroup_and_classify(test_data_rfv, ids_realizations_to_classify, r_groups, v_groups)
			
#-------------------------RFV CLASSIFIER-------------------------------------------
class RFVClassifier (Classifier):

	__metaclass__ = ABCMeta
	
	
	def __init__(self, vocab_size):
		self.vocab_size = vocab_size
		
	
	'''
	train the classifier on the given train data in the rfv format
	'''
	@abstractmethod
	def train(self, train_data_rfv):
		return None
	

	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	id_feature_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	@abstractmethod
	def classify_with_no_regroup(self, test_data_rfv, id_feature_to_classify,v_groups):
		return None
	
	
	'''
	classify the test set elements and then regroup the classified elements according to their group to decide a common class for them
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	r_groups: [[id1_groupe1,...,id_n1_groupe1],...,[id_1_groupem, ..., id_nm_groupem]] group of records that get a common classification
	v_groups: list containing the list of values that should be considered as unique classification class
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list that contains the scores corresponding to the decided features
	'''
	@abstractmethod	
	def regroup_and_classify(self, test_data_rfv, id_feature_to_classify, r_groups, v_groups):
		return None
		
		
	def classify (self, test_data_rfv, id_feature_to_classify, r_groups, v_groups):
		if r_groups == None:
			return self.classify_with_no_regroup(test_data_rfv, id_feature_to_classify, v_groups)
			
		else:
			return self.regroup_and_classify(test_data_rfv, id_feature_to_classify, r_groups, v_groups)
			
			

			
#-------------------------RANDOM CLASSIFIER-------------------------------------------
'''
random classifier is just a classifier that chooses the classes randomly. Considered as a baseline
'''			
class RandomClassifier (MClassifier):
	time_dimention = 1
	feature_dimention = 0
	
	def __init__(self):
		Classifier.__init__(self)
		
	'''
	The random classifier do not need any training
	'''
	def train(self, train_data_matrix):
		return None
	

	'''
	classify the test set elements
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_matrix, ids_features_to_classify):
		random_classifications = []
		random_scrores = []
		classifications_nb = np.shape(test_data_matrix)[RandomClassifier.time_dimention]
		
		for i in range(0,classifications_nb):
			random_classification = random.choice(ids_features_to_classify)
			random_classifications.append(random_classification)
			random_scrores.append(0)
			
		
		return [random_classifications, random_scrores]
	
	
	'''
	classify the test set elements and then regroup the classified elements according to their group to decide a common class for them
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	groups: [[id1_groupe1,...,id_n1_groupe1],...,[id_1_groupem, ..., id_nm_groupem]]
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list that contains the scores corresponding to the decided features
	'''
	def regroup_and_classify(self, test_data_matrix, ids_features_to_classify, groups):
		random_classifications = []
		random_scrores = []
		classifications_nb = len(groups)
		
		for i in range(0,classifications_nb):
			random_classification = random.choice(ids_features_to_classify)
			random_classifications.append(random_classification)
			random_scrores.append(0)
			
		
		return [random_classifications, random_scrores]
				
		