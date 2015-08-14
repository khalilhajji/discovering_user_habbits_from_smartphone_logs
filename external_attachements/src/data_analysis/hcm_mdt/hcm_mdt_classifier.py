import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import Classifier
import numpy as np
from numpy_utils import Numpy
from classifier import RFVClassifier
from hcm_mdt import HcmMdt
import pdb
'''
--------------------------------FILE DESCRIPTION---------------------
contains 2 classifiers with a very subtle difference:

HCM_MDT_Class_Classifier: a classifier that predicts a class and give the predicted class as output
HCM_MDT_Value_Classifier: a classifier that predicts a value and give the class of the predicted value as output
'''

'''-----------------------------HCM_MDT VALUE CLASSIFIER-----------------------------------'''		
class HCM_MDT_Value_Classifier (RFVClassifier):
	#the number of hidden topics to take into account for the computation of lineraly constrained bayesian matrix factorization
	
	time_dimention = 1
	feature_dimention = 0
	def __init__(self, k, vocab_size):
		RFVClassifier.__init__(self, vocab_size)
		
		self.k = 20
		
		if k != None:
			self.k=k
		
		self.train_iter = 50; self.test_iter = 20;	
		self.hcm_mdt = None
		
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	def train(self, train_data_rfv):
		
		self.hcm_mdt = HcmMdt(train_data_rfv, self.k, self.vocab_size)
		self.hcm_mdt.fit(self.train_iter)
		
	'''
	input: testdata , feature_to_classify
	output: a matrix [nb_records, nb_values] where each row represents the different prediction confidences of each value
	'''	
	def _compute_prediction_confidences(self, test_data_rfv, id_feature_to_classify, v_groups):
		if self.hcm_mdt == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
		#fit the new data to hcm_mdt model
		[test_pi, perplexity] = self.hcm_mdt.fit_newrecords(test_data_rfv, self.test_iter)
		phi = self.hcm_mdt.P[id_feature_to_classify]

		#Pr(v|r)=sum(Pr(k|r)Pr(v|k)) = theta[r,:] . phi[:,v]
		predictions = np.dot(test_pi,phi)
		
		return predictions
	
	def compute_perplexity(self, test_data_rfv):
		if self.hcm_mdt == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
			
		
		#fit the new data to hcm_mdt model
		perplexity = self.hcm_mdt.perplexity_newrecords(test_data_rfv)
		
		return perplexity
		
	
	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	id_feature_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class, first list are ids corresponding to class 1, second list to ids corresponding to class 2, ...
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_rfv, id_feature_to_classify,v_groups):
		
		#get the prediction confidences for the different values of the indicate feature in each record r -> [nb_records, nb_values]
		predictions = self._compute_prediction_confidences(test_data_rfv, id_feature_to_classify, v_groups)
		
		winner_ids = np.argmax(predictions, 1)
		winner_scores = np.max(predictions, 1)
		
		winner_classes = [] #transform the winner values to classes
		for v in winner_ids:
			for cid, cl in enumerate(v_groups):
				if v in cl:
					winner_classes.append(cid)
					break;
		

		return [winner_classes, winner_scores]
	
	
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
	def regroup_and_classify(self, test_data_rfv, id_feature_to_classify, r_groups, v_groups):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		predictions = self._compute_prediction_confidences(test_data_rfv, id_feature_to_classify, v_groups)
		
		#now we have a matrix where the higher the value of a feature in a record is, the more this feature is 'important' in that record.
		#We decide that summing the values of different records belonging to the same group indicates the importance of the features in that group.
		#Thus, the classified feature for one group of records is the one that has the biggest sum
		winner_ids = []
		winner_scores = []
		#for each group, take the feature corresponding to the maximal value of the sum of the records belonging to the group
		for group in r_groups:
			group_record = np.prod(predictions[group, :],0)
			winner_score = np.amax(group_record)
			winner_id = np.argmax(group_record)
			
			winner_ids.append(winner_id)
			winner_scores.append(winner_score)
		
		
		winner_classes = [] #transform the winner values to classes
		for v in winner_ids:
			for cid, cl in enumerate(v_groups):
				if v in cl:
					winner_classes.append(cid)
					break;
		

		return [winner_classes, winner_scores]
		
'''*****************************-------------------------***********************************
--------------------------------hcm_mdt Class CLASSIFIER-----------------------------------
********************************-------------------------***********************************'''		
class HCM_MDT_Class_Classifier (RFVClassifier):
	#the number of hidden topics to take into account for the computation of lineraly constrained bayesian matrix factorization
	
	time_dimention = 1
	feature_dimention = 0
	def __init__(self, k, vocab_size):
		RFVClassifier.__init__(self, vocab_size)
		
		self.k = 20
		
		if k != None:
			self.k=k
		
		self.train_gibbsiter = 10
		self.train_hyperparamsiter = 25
		self.test_hyperparamsiter = 20; self.test_gibbsiter = 1; self.test_chainnb=1;
			
		self.hcm_mdt = None
		
	
	
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	def train(self, train_data_rfv):
		self.hcm_mdt = HcmMdt(train_data_rfv, self.k, self.vocab_size)
		self.hcm_mdt.gibbs_iter = self.train_gibbsiter; self.hcm_mdt.hyperparams_iter = self.train_hyperparamsiter
		self.hcm_mdt.compute()
		
		
	'''
	input: testdata , feature_to_classify
	output: a matrix [nb_records, nb_values] where each row represents the different prediction confidences of each value
	'''	
	def _compute_prediction_confidences(self, test_data_rfv, id_feature_to_classify, v_groups):
		if self.hcm_mdt == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
			
		
		#fit the new data to hcm_mdt model
		[test_pi, perplexity] = self.hcm_mdt.hcm_mdt.fit_newrecords(test_data_rfv, self.test_hyperparamsiter, self.test_gibbsiter, self.test_chainnb)

		phi = self.hcm_mdt.P[id_feature_to_classify]
		
		
	
		
		#Pr(v|r)=sum(Pr(k|r)Pr(v|k)) = theta[r,:] . phi[:,v]
		predictions = np.dot(test_pi,phi)
		
	
		
		group_predictions = np.zeros((np.shape(predictions)[0], len(v_groups)))
			
		for (i,group) in enumerate(v_groups): #PREDICT THE MOST PROBABLE CLASS BY SUMMING OVER THE VALUES BELONGING TO THE SAME CLASS
			group_predictions[:,i] = np.sum(predictions[:,group],1) 

		return group_predictions
		
	
	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	id_feature_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class, first list are ids corresponding to class 1, second list to ids corresponding to class 2, ...
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_rfv, id_feature_to_classify,v_groups):
		
		#get the prediction confidences for the different values of the indicate feature in each record r -> [nb_records, nb_values]
		predictions = self._compute_prediction_confidences(test_data_rfv, id_feature_to_classify, v_groups)
		
		winner_ids = np.argmax(predictions, 1)
		winner_scores = np.max(predictions, 1)
		

		return [winner_ids, winner_scores]
	
	
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
	def regroup_and_classify(self, test_data_rfv, id_feature_to_classify, r_groups, v_groups):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		predictions = self._compute_prediction_confidences(test_data_rfv, id_feature_to_classify, v_groups)
		
		#now we have a matrix where the higher the value of a feature in a record is, the more this feature is 'important' in that record.
		#We decide that summing the values of different records belonging to the same group indicates the importance of the features in that group.
		#Thus, the classified feature for one group of records is the one that has the biggest sum
		winner_ids = []
		winner_scores = []
		#for each group, take the feature corresponding to the maximal value of the sum of the records belonging to the group
		for group in r_groups:
			group_record = np.prod(predictions[group, :],0)
			winner_score = np.amax(group_record)
			winner_id = np.argmax(group_record)
			
			winner_ids.append(winner_id)
			winner_scores.append(winner_score)
		
		
		return [winner_ids, winner_scores]