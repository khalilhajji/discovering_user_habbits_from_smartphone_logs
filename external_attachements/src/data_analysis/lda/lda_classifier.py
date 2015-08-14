import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import Classifier
import numpy as np
from numpy_utils import Numpy
from classifier import RVClassifier
import pdb
from lda import Lda
'''
--------------------------------FILE DESCRIPTION---------------------
contains 2 classifiers with a very subtle difference:

LDA_Class_Classifier: a classifier that predicts a class and give the predicted class as output
LDA_Value_Classifier: a classifier that predicts a value and give the class of the predicted value as output
'''

'''-----------------------------GHCM_MDT VALUE CLASSIFIER-----------------------------------'''		
class LDA_Value_Classifier (RVClassifier):
	#the number of hidden topics to take into account for the computation of lineraly constrained bayesian matrix factorization
	
	def __init__(self, k, vocab_size):
		RVClassifier.__init__(self, vocab_size)
		
		self.k = 20
		
		if k != None:
			self.k=k
		
		self.train_gibbsiter = 40; self.nb_averages = 3;
		self.train_hyperparamsiter = 25
		self.test_hyperparamsiter = 20; self.test_gibbsiter = 1; self.test_chainnb=5;
		
			
		self.lda = None
		
	
	
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	def train(self, train_data_rv):
		
		self.lda = Lda(train_data_rv, self.k, self.vocab_size)
		self.lda.gibbs_iter = self.train_gibbsiter; self.lda.hyperparams_iter = self.train_hyperparamsiter;
		self.lda.hyper_parameter_number_of_samples_to_average = self.nb_averages
		self.lda.fit(self.train_hyperparamsiter, self.train_gibbsiter)
		#pdb.set_trace()
		
	'''
	input: testdata , feature_to_classify
	output: a matrix [nb_records, nb_values] where each row represents the different prediction confidences of each value
	'''	
	def _compute_prediction_confidences(self, test_data_rv, ids_realizations_to_classify, v_groups):
		if self.lda == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
			
		
		#fit the new data to lda model
		[test_theta, perplexity] = self.lda.fit_newrecords(test_data_rv, self.test_hyperparamsiter, self.test_gibbsiter, self.test_chainnb)
		phi = self.lda.phi[:,ids_realizations_to_classify]
		#pdb.set_trace()
		#Pr(v|r)=sum(Pr(k|r)Pr(v|k)) = theta[r,:] . phi[:,v]
		predictions = np.dot(test_theta,phi)
		
		return predictions
	
	def compute_perplexity(self, test_data_rfv):
		raise Exception("Not implemented exception")
		return None
		
	
	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	ids_realizations_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class, first list are ids corresponding to class 1, second list to ids corresponding to class 2, ...
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_rfv, ids_realizations_to_classify,v_groups):
		
		#get the prediction confidences for the different values of the indicate feature in each record r -> [nb_records, nb_values]
		predictions = self._compute_prediction_confidences(test_data_rfv, ids_realizations_to_classify, v_groups)
		
		winner_ranks = np.argmax(predictions, 1)
		winner_ids = np.asarray([ids_realizations_to_classify[rank] for rank in winner_ranks])
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
	def regroup_and_classify(self, test_data_rfv, ids_realizations_to_classify, r_groups, v_groups):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		predictions = self._compute_prediction_confidences(test_data_rfv, ids_realizations_to_classify, v_groups)
		
		winner_ranks = []
		winner_scores = []
		#for each group, take the feature corresponding to the maximal value of the sum of the records belonging to the group
		for group in r_groups:
			group_record = np.prod(predictions[group, :],0)
			winner_score = np.amax(group_record)
			winner_id = np.argmax(group_record)
			
			winner_ranks.append(winner_id)
			winner_scores.append(winner_score)
		
		winner_ids = np.asarray([ids_realizations_to_classify[rank] for rank in winner_ranks])
		
		winner_classes = [] #transform the winner values to classes
		for v in winner_ids:
			for cid, cl in enumerate(v_groups):
				if v in cl:
					winner_classes.append(cid)
					break;
		

		return [winner_classes, winner_scores]
		
'''*****************************-------------------------***********************************
--------------------------------GHCM_MDT Class CLASSIFIER-----------------------------------
********************************-------------------------***********************************'''		
class LDA_Class_Classifier (RVClassifier):
	#the number of hidden topics to take into account for the computation of lineraly constrained bayesian matrix factorization
	
	def __init__(self, k, vocab_size):
		RVClassifier.__init__(self, vocab_size)
		
		self.k = 20
		
		if k != None:
			self.k=k
		
		self.train_gibbsiter = 1; self.nb_averages = 1;
		self.train_hyperparamsiter = 1
		self.test_hyperparamsiter = 1; self.test_gibbsiter = 1; self.test_chainnb=1;
		
			
		self.lda = None
		
	
	
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	def train(self, train_data_rv):
		
		self.lda = Lda(train_data_rv, self.k, self.vocab_size)
		self.lda.gibbs_iter = self.train_gibbsiter; self.lda.hyperparams_iter = self.train_hyperparamsiter;
		self.lda.hyper_parameter_number_of_samples_to_average = self.nb_averages
		self.lda.fit(self.train_hyperparamsiter, self.train_gibbsiter)
		
	'''
	input: testdata , feature_to_classify
	output: a matrix [nb_records, nb_values] where each row represents the different prediction confidences of each value
	'''	
	def _compute_prediction_confidences(self, test_data_rfv, ids_realizations_to_classify, v_groups):
		if self.lda == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
			
		
		#fit the new data to lda model
		[test_theta, perplexity] = self.lda.fit_newrecords(test_data_rv, self.test_hyperparamsiter, self.test_gibbsiter, self.test_chainnb)
		phi = self.lda.phi[:,ids_realizations_to_classify]
		
		
	
		
		#Pr(v|r)=sum(Pr(k|r)Pr(v|k)) = theta[r,:] . phi[:,v]
		predictions = np.dot(test_theta,phi)
		
	
		min_id = np.min(ids_realizations_to_classify)
		group_predictions = np.zeros((np.shape(predictions)[0], len(v_groups)))
			
		for (i,group) in enumerate(v_groups): #PREDICT THE MOST PROBABLE CLASS BY SUMMING OVER THE VALUES BELONGING TO THE SAME CLASS
			shifted_group = np.asarray(group) - min_id
			group_predictions[:,i] = np.sum(predictions[:,group],1) 

		return group_predictions
		
	
	'''
	classify the test set elements
	test_data_rfv: test data in the rfv format
	ids_realizations_to_classify: the if of the feature to be classified (note that this feature must be absent from all the test records)
	v_groups: list containing the list of values that should be considered as unique classification class, first list are ids corresponding to class 1, second list to ids corresponding to class 2, ...
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_rfv, ids_realizations_to_classify,v_groups):
		
		#get the prediction confidences for the different values of the indicate feature in each record r -> [nb_records, nb_values]
		predictions = self._compute_prediction_confidences(test_data_rfv, ids_realizations_to_classify, v_groups)
		
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
	def regroup_and_classify(self, test_data_rfv, ids_realizations_to_classify, r_groups, v_groups):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		predictions = self._compute_prediction_confidences(test_data_rfv, ids_realizations_to_classify, v_groups)
		
		
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