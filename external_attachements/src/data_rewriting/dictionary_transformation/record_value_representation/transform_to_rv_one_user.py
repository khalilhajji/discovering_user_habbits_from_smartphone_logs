#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
import numpy as np
import collections
from numpy_utils import Numpy
from rfv_data_utils import RVFDataExtractor
from rv_data_utils import RVDataExtractor
import pdb


def transform_to_rv_one_user(user_id):
	
		
	print "loading data for user "+str(user_id)
	[rfv, featuresnames, valuesnames, recordsdates] = RVFDataExtractor.load_rvf(user_id)
	
	
	realization_names = []
	rvid_table = dict()
	id = 0
	for f in valuesnames:
		f_name = featuresnames[f]
		rvid_table[f]=dict()
		for v, v_name in enumerate(valuesnames[f]):
			realization_names += [f_name+"__"+v_name]
			rvid_table[f][v]=id
			id+=1
	
	rv_data = dict()
	for r in rfv:
		rv_data[r] = []
		for f in rfv[r]:
			for v in rfv[r][f]:
				rv_data[r] += [rvid_table[f][v]]
				
	#pdb.set_trace()
	
	RVDataExtractor.save_rv(user_id, rv_data, realization_names, recordsdates)
	

	
	