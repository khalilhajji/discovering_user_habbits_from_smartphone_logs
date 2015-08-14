
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
from perplexity_evaluator import PerplexityEvaluator
import pdb

'''
This evaluation Method uses the Feature prediction metric: it evaluates how well a classifier is able to predict a hidden feature from the test data
1- the evaluated classifier is trained with a train set containing the feature to predict
2- the feature to predict is removed from the test set
3- the evaluated classifier tries to guess the value of the hidden feature from the test samples
'''
class RfvPerplexityEvaluator(PerplexityEvaluator):
	#rate of the training set with respect to the total dataset
	train_size = 0.8
	
	#in the name of the feature to predict
	feature_to_predict = None
	
	
	def __init__(self, rfv_data, features, values, train_ids, test_ids):
		#the data_matrix
		self.rfv_data = rfv_data
		self.fnames = features
		self.vnames = values
		
		
		#split the dataset into train and test set
		self.train_ids = train_ids; self.test_ids = test_ids
		if self.train_ids == None:
			[self.train_rfv, self.test_rfv, self.train_ids, self.test_ids] = self._build_train_test_dataset(RfvPerplexityEvaluator.train_size)
		else:
			[self.train_rfv, self.test_rfv] = self._apply_train_test_split(self.train_ids, self.test_ids)
		
		#pdb.set_trace()
			
		
		
			
		
		
	
	'''
	This method evaluates the selected classifier and returns its accuracy on a test set
	returns [good_predictions, total_predictions, accuracy]
	'''
	def evaluate(self, classifier) :
		
		
		#train the classifier on the trainset
		classifier.train(self.train_rfv)
		
		#evaluate the classifier on the testset
		perplexity = classifier.compute_perplexity(self.test_rfv)
	
		
		return perplexity
	
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