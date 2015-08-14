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


class PerplexityEvaluator(object):
	__metaclass__ = ABCMeta
	
	'''
	This method evaluates the selected classifier and returns its accuracy on a test set
	returns perplexity
	'''
	@abstractmethod
	def evaluate(self, classifier) :
		return None
