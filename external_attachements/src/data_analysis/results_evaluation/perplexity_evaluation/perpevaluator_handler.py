#!/usr/bin/env python
import sys
from abc import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import Classifier
from classifier import *
from rfv_perplexity_evaluator import * 



class PerpEvaluatorHandler(object):
	
	
	def __init__(self):
		self.evaluators = {}
		self.train_ids = None
		self.test_ids = None
		
	def instanciate_rvf(self, RfvPerplexityEvaluator, rfv_data, features, values):
		rfv_fpe = RfvPerplexityEvaluator(rfv_data, features, values, self.train_ids, self.test_ids)
		[self.train_ids, self.test_ids] = [rfv_fpe.train_ids, rfv_fpe.test_ids]
		rate = len(self.train_ids)*1.0/(len(self.train_ids)+len(self.test_ids))*1.0
		print "(trainsize, testsize,rate) : ("+str(len(self.train_ids))+","+str(len(self.test_ids))+","+str(rate)+")"
		self.evaluators[RfvPerplexityEvaluator] = rfv_fpe
	
	def instanciate_rv (self, RvPerplexityEvaluator, matrix, row_labels, columns_labels):
		m_fpe = RvPerplexityEvaluator(matrix, row_labels, columns_labels, self.train_ids, self.test_ids)
		[self.train_ids, self.test_ids] = [m_fpe.train_ids, m_fpe.test_ids]
		rate = len(self.train_ids)*1.0/(len(self.train_ids)+len(self.test_ids))*1.0
		print "(trainsize, testsize,rate) : ("+str(len(self.train_ids))+","+str(len(self.test_ids))+","+str(rate)+")"
		self.evaluators[RvPerplexityEvaluator] = m_fpe
	
	
	def evaluate(self, classifier):
		if isinstance(classifier, RFVClassifier):
			for type, evaluator in self.evaluators.iteritems():
				if issubclass(type, RfvPerplexityEvaluator):
					return evaluator.evaluate(classifier)
		
		
		elif isinstance(classifier, RVClassifier):
			for type, evaluator in self.evaluators.iteritems():
				if issubclass(type, RvPerplexityEvaluator):
					return evaluator.evaluate(classifier)
	