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


class FeaturePredictionEvaluator(object):
	__metaclass__ = ABCMeta
	
	feature_not_present_id = -1
	unknown_class_id = -1
	
	
	'''
	This method evaluates the selected classifier and returns its accuracy on a test set
	returns [good_predictions, total_predictions, accuracy, accuracy_class1, ..., accuracy_classm]
	'''
	@abstractmethod
	def evaluate(self, classifier) :
		return None
		
	

	def _compute_accuracy(self, predicted_classes, ground_truth):
		nb = 0
		good_predictions = 0
		for predicted_class in predicted_classes:
			#compute the accuracy only in the records that have a known class (eliminate the ones that have unknown class)
			if FeaturePredictionEvaluator.unknown_class_id not in ground_truth[nb]:
				if predicted_class in ground_truth[nb]:
					good_predictions +=1
				nb +=1
			
		total_predictions = len(ground_truth)*1.0
		
		return [good_predictions, total_predictions, good_predictions/total_predictions]
		
	
	
	def _compute_macro_average_accuracy(self, predicted_classes, ground_truth):
		nb = 0
		accuracy_by_class = {}
		
		#initialize the accuracy by class dict
		#the keys are the class ids
		# each value contains a 3 cells list representing [good_predictions, total_realizations, accuracy] for the concerned class
		for class_labels in ground_truth:
			for class_label in class_labels:
				if class_label not in accuracy_by_class:
					#each entry contains is initialized to [good_predictions, total_realizations, accuracy] [0,0,0]
					accuracy_by_class[class_label] = [0.0, 0.0, 0.0]
		
		
		for predicted_class in predicted_classes:
			#compute the accuracy only in the records that have a known class (eliminate the ones that have unknown class)
			if FeaturePredictionEvaluator.unknown_class_id not in ground_truth[nb]:
				if predicted_class in ground_truth[nb]:
					#we have a correct prediction
					the_class = predicted_class
					#increase good predictions by 1
					accuracy_by_class[the_class][0] +=1
					#increase total_realizations by 1
					accuracy_by_class[the_class][1] +=1
					#update the accuracy
					accuracy_by_class[the_class][2] =accuracy_by_class[the_class][0]/accuracy_by_class[the_class][1]
				
				else:
					#we have a bad prediction-> chose one ground_truth class and add to it a realization
					true_class = ground_truth[nb][0]
					#increase total_realizations by 1
					accuracy_by_class[true_class][1] +=1
					#update the accuracy
					accuracy_by_class[true_class][2] =accuracy_by_class[true_class][0]/accuracy_by_class[true_class][1]
				nb +=1
		

		accuracy_by_class = collections.OrderedDict(sorted(accuracy_by_class.items(), key=lambda x: x[0]))
		print "accuracy by class dict : "
		print accuracy_by_class
		#compute the macro average, which is the average accuracy over all the classes
		class_nb = 0.0
		macro_accuracy = 0.0
		class_accuracies = []
		for a_class, class_results in accuracy_by_class.iteritems():
			macro_accuracy += class_results[2]
			class_nb+=1
			class_accuracies.append(class_results[2])
			
		macro_accuracy = macro_accuracy/class_nb
		
		result = [macro_accuracy]+class_accuracies
		
		#list containing [macro_averaging_accuracy, accuracy_class1, accuracy_class2,..., accuracy_classn]
		print "macro_averaging accuracy result"
		print result
		return result