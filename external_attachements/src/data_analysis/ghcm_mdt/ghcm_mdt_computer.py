#!/usr/bin/env python
import sys
import collections
import pprint as pp
import copy
from datetime import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from categorized_data_utils import *
from json_utils import JsonUtils
from date_time_utils import DateTimeUtils
import math
import numpy as np
from datetime import datetime, timedelta
from ghcm_mdt import *
import collections



'''

'''
class GHCM_MDTComputer (object):
	k_label = "hidden_classes"
	
	'''
	possible values for:
		pretransformation_name : {"none" ,"idf", "ldc","idc","idf3", None}
		a_constrains_name : { "[0,1]", None}
		b_constrains_name : {"positive, sum=1", None}
	'''
	def __init__(self, rfv_data, k, vocab_size):
		self.gibbs_iter = 50
		self.hyperparams_iter = 25
		self.rfv_data = rfv_data
		self.k = 10
		
		if k!= None:
			self.k = k
		
		#distribution of different values in the hidden classes
		#dictionary data[feature_id]: Array [nb_hclass, voc_size] that associates to
        #each value that can be taken by feature f a probability to appear in hidden
        #class k
		self.phi = None
		
		#distribution of the different hidden classes in the records
		#Array [nb_records, nb_hclass] that associates to each record the mix coeffs
        #over hidden classes
		self.theta = None
		
		#the log likelihood
		self.perplexity = None
		
		
		self.ghcm_mdt = GhcmMdt(rfv_data, k, vocab_size)
		self.ghcm_mdt.hyper_parameter_number_of_samples_to_average = 5
		
		
		
		self.rows_interpretable_output = {}
		
		
	def compute(self):
		#run the ghcm_mdt on the data
		print("start fitting GHCM_MDT model with (hyperparams_iter, gibbs_iter)=("+str(self.hyperparams_iter)+","+str(self.gibbs_iter)+") and k="+str(self.k))
		self.perplexity = self.ghcm_mdt.fit(self.hyperparams_iter, self.gibbs_iter)
		print("end fitting")
		
		self.phi = self.ghcm_mdt.phi
		self.theta = self.ghcm_mdt.theta
		
		return [self.phi, self.theta]
		
	
	'''
	Call this method to construct a humanely readable clusters result. They are represented as a dictionary stored in the class attribute rows_interpretable_output
	from the realization and the id_info returns the label of this realization 
	nb_features_display: for each concept the number of features to display
	'''
	def construct_rows_interpretable_output(self, features_names, values_names, nb_features_display):
		#built the interpretable output as a dictionary
		self.rows_interpretable_output[GHCM_MDTComputer.k_label] = {}
		nb_hclasses = self.k
		
		for k in range(nb_hclasses):	#fill rows_interpretable_output
			k_importance = np.sum(self.theta[:,k])/np.size(self.theta,0)	#the probability of class k to appear in the corpus = sumi(Pr(k|ri)*Pr(ri))=sumi(Pr(k|ri)*1/R)
			self.rows_interpretable_output[GHCM_MDTComputer.k_label][k_importance] = {}   #each hidden class has its importance as label
			
			for f in self.phi :                   #fill values distribution for hidden class k for each feature
				scores = self.phi[f][k][:]        #values distribution for feature f in hidden class k
				d_scores = {}
				for v in range(len(scores)):			  #associate to each value its name
					d_scores[unicode(values_names[f][v])]=scores[v]
				print "scores of feature "+str(features_names[f])+" and topic "+str(k)
				print "phi "+str(self.phi[f][k])
				d_scores = collections.OrderedDict(sorted(d_scores.items(), key=lambda item: item[1], reverse= True)[0:min(nb_features_display, len(scores))]) #sort the values by importance
				print "labeled scores "+str(d_scores)
				self.rows_interpretable_output[GHCM_MDTComputer.k_label][k_importance][unicode(features_names[f])]=d_scores  #add feature f to the hidden class k
		
		self.rows_interpretable_output[GHCM_MDTComputer.k_label] = collections.OrderedDict(sorted(self.rows_interpretable_output[GHCM_MDTComputer.k_label].items(), key=lambda item: item[0], reverse= True))
		print "labeled scores "+str(self.rows_interpretable_output[GHCM_MDTComputer.k_label])
		
		return self.rows_interpretable_output
		
		
		
		
	
				
		