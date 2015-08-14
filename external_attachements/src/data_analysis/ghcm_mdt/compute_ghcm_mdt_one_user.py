#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from numpy_utils import Numpy
from rfv_data_utils import RVFDataExtractor
from ghcm_mdt_computer import GHCM_MDTComputer
from logs_file_writer import JsonLogsFileWriter
'''

'''
disp_k = 20
disp_m = 20
do_laplace_smoothing = True
time_dimention = 1
def compute_ghcm_mdt_one_user(user_id):
	file_name = "ghcm_mdt_user_"+str(user_id)
	print "loading matrix user "+str(user_id)+"..."
	[rfvdata, featuresnames, valuesnames, recordsdates] = RVFDataExtractor.load_rvf(user_id)
	print "values" + JsonUtils.dict_as_json_str(valuesnames)
	print "data" + JsonUtils.dict_as_json_str(rfvdata[0])
	vocab_size = [len(valuesnames[f]) for f in range(len(valuesnames.keys()))]
	print "user "+str(user_id)+" has "+str(len(featuresnames))+" features and "+str(len(rfvdata))+" records"
	print "features names"
	print featuresnames
	
	print "values" + JsonUtils.dict_as_json_str(valuesnames)
	for k in [10,20,30]:
		#compute the ghcm_mdt
		ghcm_mdt_comp = GHCM_MDTComputer(rfvdata, k, vocab_size)
		print "computing SVD for user "+str(user_id)+"..."
		ghcm_mdt_comp.compute()
		
		print "constructing interpretable output for user "+str(user_id)+"..."
		ghcm_mdt_comp.construct_rows_interpretable_output(featuresnames, valuesnames, disp_m)
		r_output = ghcm_mdt_comp.rows_interpretable_output
		
		#write the result
		print "writing SVD result for user "+str(user_id)+"..."
		JsonLogsFileWriter.write(r_output, file_name)
	
	
	
	
	
		
	
	
	