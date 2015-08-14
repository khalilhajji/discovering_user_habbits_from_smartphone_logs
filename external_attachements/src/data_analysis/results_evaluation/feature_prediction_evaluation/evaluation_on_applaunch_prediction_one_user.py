#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/singular_value_decomposition")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/linearly_constrained_basyesian_mf")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/ghcm_mdt")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/hcm_mdt")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/lda")
from classifier import *
from json_utils import JsonUtils
from numpy_utils import Numpy
from rfv_data_utils import RVFDataExtractor
from rv_data_utils import RVDataExtractor
from lda_classifier import LDA_Value_Classifier
from hcm_mdt_classifier import HCM_MDT_Value_Classifier
from ghcm_mdt_classifier import GHCM_MDT_Value_Classifier
from rv_feature_prediction_evaluator import RvApplaunchPredictionEvaluator
from rfv_feature_prediction_evaluator import RfvApplaunchPredictionEvaluator 
from fpevaluator_handler import FpEvaluatorHandler
import random as rnd

def evaluation_on_applaunch_prediction_one_user(user_id):
	print "loading rfv user "+str(user_id)+"..."
	[rfvdata, featuresnames, valuesnames, recordsdates] = RVFDataExtractor.load_rvf(user_id)
	vocab_size = [len(valuesnames[f]) for f in range(len(valuesnames.keys()))]
	print "user "+str(user_id)+" has "+str(len(rfvdata))+" records"
	
	print "loading rv user "+str(user_id)+"..."
	[rv_data, realizationsnames, recordsdates] = RVDataExtractor.load_rv(user_id)
	realization_size = len(realizationsnames)
	
	
	classifiers = {"Random ": RandomClassifier()}#add the random classifier
	classifiers = {"Most Frequent ": HCM_MDT_Value_Classifier(1, vocab_size)}#add the most frequent classifier
	
	
	'''
	for k in range(1,21):
		classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size) #add a ghcmdt classifier for each k
		classifiers["LCBMF k="+str(k)] = LCBMFClassifier(None, None, None, k) #add a lcbmf classifier for each k
		 #add a svd classifier for each k'''
		
	'''for k in [1,10,20,30,40,50,60]:
		c =GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["GHCM_MDT k="+str(k)] = c'''
		
	for k in [1,10,20,30,50,70]:
		classifiers["LDA k="+str(k)] = LDA_Value_Classifier(k, realization_size)
		classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["HCM_MDT k="+str(k)] = HCM_MDT_Value_Classifier(k, vocab_size)
		
	
	eval_handler = FpEvaluatorHandler()
	eval_handler.instanciate_rvf (RfvApplaunchPredictionEvaluator, rfvdata, featuresnames, valuesnames)
	eval_handler.instantiate_rv(RvApplaunchPredictionEvaluator,rv_data, realizationsnames)
	
	evaluations = {}
	nb=1
	for name, classifier in classifiers.iteritems():
		print "evaluating "+name+" on user "+str(user_id)+" nb "+str(nb)+"/"+str(len(classifiers))
		#results = [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
		results = eval_handler.evaluate(classifier)
		evaluations[name] = results
		nb+=1
		
		
	classes = 	eval_handler.classes
	return [evaluations, classes]	