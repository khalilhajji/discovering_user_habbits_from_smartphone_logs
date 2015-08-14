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
from classifier import *
from m_feature_prediction_evaluator import *
from rfv_feature_prediction_evaluator import * 
from rv_feature_prediction_evaluator import *



class FpEvaluatorHandler(object):
	
	
	def __init__(self):
		self.evaluators = {}
		self.train_ids = None
		self.test_ids = None
		self.classes = None
		
	def instanciate_rvf(self, RfvFeaturePredictionEvaluator, rfv_data, features, values):
		rfv_fpe = RfvFeaturePredictionEvaluator(rfv_data, features, values, self.train_ids, self.test_ids)
		[self.train_ids, self.test_ids] = [rfv_fpe.train_ids, rfv_fpe.test_ids]
		rate = len(self.train_ids)*1.0/(len(self.train_ids)+len(self.test_ids))*1.0
		print "(trainsize, testsize,rate) : ("+str(len(self.train_ids))+","+str(len(self.test_ids))+","+str(rate)+")"
		self.classes = RfvFeaturePredictionEvaluator.class_names
		self.evaluators[RfvFeaturePredictionEvaluator] = rfv_fpe
		
	def instantiate_rv(self, RvFeaturePredictionEvaluator,rv_data, values):
		rv_fpe = RvFeaturePredictionEvaluator(rv_data, values, self.train_ids, self.test_ids)
		[self.train_ids, self.test_ids] = [rv_fpe.train_ids, rv_fpe.test_ids]
		rate = len(self.train_ids)*1.0/(len(self.train_ids)+len(self.test_ids))*1.0
		print "(trainsize, testsize,rate) : ("+str(len(self.train_ids))+","+str(len(self.test_ids))+","+str(rate)+")"
		self.classes = RvFeaturePredictionEvaluator.class_names
		self.evaluators[RvFeaturePredictionEvaluator] = rv_fpe
	
	def instanciate_m (self, MFeaturePredictionEvaluator, matrix, row_labels, columns_labels):
		m_fpe = MFeaturePredictionEvaluator(matrix, row_labels, columns_labels, self.train_ids, self.test_ids)
		[self.train_ids, self.test_ids] = [m_fpe.train_ids, m_fpe.test_ids]
		rate = len(self.train_ids)*1.0/(len(self.train_ids)+len(self.test_ids))*1.0
		print "(trainsize, testsize,rate) : ("+str(len(self.train_ids))+","+str(len(self.test_ids))+","+str(rate)+")"
		self.classes = MFeaturePredictionEvaluator.classes
		self.evaluators[MFeaturePredictionEvaluator] = m_fpe
	
	
	def evaluate(self, classifier):
		if isinstance(classifier, RFVClassifier):
			for type, evaluator in self.evaluators.iteritems():
				if issubclass(type, RfvFeaturePredictionEvaluator):
					return evaluator.evaluate(classifier)
		
		
		elif isinstance(classifier, MClassifier):
			for type, evaluator in self.evaluators.iteritems():
				if issubclass(type, MFeaturePredictionEvaluator):
					return evaluator.evaluate(classifier)
					
		elif isinstance(classifier, RVClassifier):
			for type, evaluator in self.evaluators.iteritems():
				if issubclass(type, RvFeaturePredictionEvaluator):
					return evaluator.evaluate(classifier)
			
	