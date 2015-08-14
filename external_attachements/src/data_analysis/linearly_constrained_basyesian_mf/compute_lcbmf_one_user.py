#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from numpy_utils import Numpy
from matrix_data_utils import *
from lcbmf_computer import LCBMFComputer
from logs_file_writer import JsonLogsFileWriter
'''

'''
disp_m = 20
time_dimention = 1
def compute_lcbmf_one_user(user_id):
	file_name = "lcbmf_user_"+str(user_id)
	print "loading matrix user "+str(user_id)+"..."
	data_matrix = MDataExtractor.load_matrix(user_id)
	rows_labels =  MDataExtractor.load_labels_vector(user_id)
	columns_labels = MDataExtractor.load_time_vector(user_id)
	importance_scores = MDataExtractor.load_importance_scores(user_id)
	
	print "user "+str(user_id)+" has "+str(len(rows_labels))+" features (rows) and "+str(len(columns_labels))+" realization (columns)"
	
	#compute the lcbmf
	lcbmf_comp = LCBMFComputer(data_matrix, "idf", "[0,1]", "positive, sum=1", 10)
	print "computing LCBMF for user "+str(user_id)+"..."
	lcbmf_comp.compute()
	
	
	print "constructing interpretable output for user "+str(user_id)+"..."
	lcbmf_comp.construct_rows_interpretable_output(rows_labels, disp_m)
	r_output = lcbmf_comp.rows_interpretable_output
	
	#write the result
	print "writing LCBMF result for user "+str(user_id)+"..."
	JsonLogsFileWriter.write(r_output, file_name)
	
	
	
	
	
		
	
	
	