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
from matrix_data_utils import *
from rfv_data_utils import RVFDataExtractor
from rv_data_utils import RVDataExtractor
from svd_classifier import SVDClassifier
from lcbmf_classifier import LCBMFClassifier
from ghcm_mdt_classifier import GHCM_MDT_Value_Classifier
from lda_classifier import LDA_Value_Classifier
from hcm_mdt_classifier import HCM_MDT_Value_Classifier

from rv_feature_prediction_evaluator import RvLocationPredictionEvaluator
from m_feature_prediction_evaluator import MLocationPredictionEvaluator
from rfv_feature_prediction_evaluator import RfvLocationPredictionEvaluator 
from fpevaluator_handler import FpEvaluatorHandler
import random as rnd
'''

'''
def evaluation_on_location_prediction_one_user(user_id):
	
	print "loading matrix user "+str(user_id)+"..."
	data_matrix = MDataExtractor.load_matrix(user_id)
	rows_labels =  MDataExtractor.load_labels_vector(user_id)
	columns_labels = MDataExtractor.load_time_vector(user_id)
	importance_scores = MDataExtractor.load_importance_scores(user_id)
	print "user "+str(user_id)+" has "+str(len(rows_labels))+" features (rows) and "+str(len(columns_labels))+" realization (columns)"
	
	print "loading rfv user "+str(user_id)+"..."
	[rfvdata, featuresnames, valuesnames, recordsdates] = RVFDataExtractor.load_rvf(user_id)
	vocab_size = [len(valuesnames[f]) for f in range(len(valuesnames.keys()))]
	print "user "+str(user_id)+" has "+str(len(rfvdata))+" records"
	
	print "loading rv user "+str(user_id)+"..."
	[rv_data, realizationsnames, recordsdates] = RVDataExtractor.load_rv(user_id)
	realization_size = len(realizationsnames)
	
	
	classifiers = {"Random ": RandomClassifier()}#add the random classifier
	classifiers = {"Most Frequent ": SVDClassifier("idf", 1)}#add the most frequent classifier
	
	'''
	for k in range(1,21):
		classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size) #add a ghcmdt classifier for each k
		classifiers["LCBMF k="+str(k)] = LCBMFClassifier(None, None, None, k) #add a lcbmf classifier for each k
		classifiers["SVD k="+str(k)] = SVDClassifier("idf", k) #add a svd classifier for each k'''
		
	'''for k in [1,10,20,30,40,50,60]:
		c =GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["GHCM_MDT k="+str(k)] = c'''
		
	'''for k in [10,15,20,25,30,35]:
		c =GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["GHCM_MDT k="+str(k)] = c'''
		
	for k in [1,10,20,30,50,70]:
		classifiers["SVD k="+str(k)] = SVDClassifier("idf", k)
		classifiers["LDA k="+str(k)] = LDA_Value_Classifier(k, realization_size)
		classifiers["HCM_MDT k="+str(k)] = HCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["LCBMF k="+str(k)] = LCBMFClassifier(None, None, None, k)
		
	
	eval_handler = FpEvaluatorHandler()
	eval_handler.instanciate_m (MLocationPredictionEvaluator, data_matrix, rows_labels, columns_labels)
	eval_handler.instanciate_rvf (RfvLocationPredictionEvaluator, rfvdata, featuresnames, valuesnames)
	eval_handler.instantiate_rv(RvLocationPredictionEvaluator,rv_data, realizationsnames)
	
	evaluations = {}
	
	for name, classifier in classifiers.iteritems():
		print "evaluating "+name+" on user "+str(user_id)
		#results = [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
		results = eval_handler.evaluate(classifier)
		evaluations[name] = results
		
		
	classes = 	eval_handler.classes
	return [evaluations, classes]
	
				
		