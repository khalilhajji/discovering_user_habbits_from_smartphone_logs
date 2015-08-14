#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/ghcm_mdt")
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/hcm_mdt")
from classifier import *
from json_utils import JsonUtils
from numpy_utils import Numpy
from ghcm_mdt_classifier import GHCM_MDT_Value_Classifier
from rfv_data_utils import RVFDataExtractor
from rfv_perplexity_evaluator import RfvPerplexityEvaluator 
from perpevaluator_handler import PerpEvaluatorHandler
from ghcm_mdt import GhcmMdt
import random as rnd
from hcm_mdt_classifier import HCM_MDT_Value_Classifier

'''

'''
def evaluation_perplexity_one_user(user_id):
	print "loading rfv user "+str(user_id)+"..."
	[rfvdata, featuresnames, valuesnames, recordsdates] = RVFDataExtractor.load_rvf(user_id)
	vocab_size = [len(valuesnames[f]) for f in range(len(valuesnames.keys()))]
	print "user "+str(user_id)+" has "+str(len(rfvdata))+" records"
	
	classifiers={}
	'''
	for k in range(1,21):
		classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size) #add a ghcmdt classifier for each k
		classifiers["LCBMF k="+str(k)] = LCBMFClassifier(None, None, None, k) #add a lcbmf classifier for each k
		classifiers["SVD k="+str(k)] = SVDClassifier("idf", k) #add a svd classifier for each k'''
	k = 8	
	for k in [1,3,5,7,10]:
		#classifiers["GHCM_MDT k="+str(k)] = GHCM_MDT_Value_Classifier(k, vocab_size)
		classifiers["HCM_MDT k="+str(k)] = HCM_MDT_Value_Classifier(k, vocab_size)
		
		
		
		
	
	eval_handler = PerpEvaluatorHandler()
	#eval_handler.instanciate_rv (MLocationPredictionEvaluator, data_matrix, rows_labels, columns_labels)
	eval_handler.instanciate_rvf (RfvPerplexityEvaluator, rfvdata, featuresnames, valuesnames)
	
	evaluations = {}
	
	for name, classifier in classifiers.iteritems():
		print "evaluating "+name+" on user "+str(user_id)
		#results = [good_predictions, total_predictions, accuracy, macro_average_acc_by_class, accuracy_class1,...,accuracy_classn]
		results = eval_handler.evaluate(classifier)
		evaluations[name] = results
		print "results for "+name+" on user "+str(user_id)+" : "+str(results)
		
		
	return evaluations
	
				
		