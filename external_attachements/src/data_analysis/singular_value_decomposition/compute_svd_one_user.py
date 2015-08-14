#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from numpy_utils import Numpy
from matrix_data_utils import *
from svd_computer import SVDComputer
from logs_file_writer import JsonLogsFileWriter
'''

'''
disp_k = 20
disp_m = 20
do_laplace_smoothing = True
time_dimention = 1
def compute_svd_one_user(user_id):
	file_name = "svd_user_"+str(user_id)
	print "loading matrix user "+str(user_id)+"..."
	data_matrix = MDataExtractor.load_matrix(user_id)
	rows_labels =  MDataExtractor.load_labels_vector(user_id)
	columns_labels = MDataExtractor.load_time_vector(user_id)
	importance_scores = MDataExtractor.load_importance_scores(user_id)
	
	print "user "+str(user_id)+" has "+str(len(rows_labels))+" features (rows) and "+str(len(columns_labels))+" realization (columns)"
	
	#do the idf / or idc transformation before computing the SVD
	print "doing idf transformation for user "+str(user_id)+"..."
	document_transformed_matrix = np.copy(data_matrix)
	[document_transformed_matrix, scores] = Numpy.idf_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	#[document_transformed_matrix, scores] = Numpy.idc_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	#[document_transformed_matrix, scores] = Numpy.idf3_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	#[document_transformed_matrix, scores] = Numpy.ldc_matrix_transformation(data_matrix, time_dimention)
	
	term_transformed_matrix = np.ones(np.shape(data_matrix))
	#term_transformed_matrix = Numpy.ti_matrix_transformation(data_matrix, importance_scores)	
	#term_transformed_matrix = Numpy.nti_matrix_transformation(data_matrix,  importance_scores)
	
	data_matrix = document_transformed_matrix * term_transformed_matrix
	
	#compute the SVD
	svd_comp = SVDComputer(data_matrix, rows_labels, columns_labels)
	print "computing SVD for user "+str(user_id)+"..."
	svd_comp.compute_svd()
	
	print "constructing interpretable output for user "+str(user_id)+"..."
	energy_captured = svd_comp.construct_rows_interpretable_output(disp_k, disp_m)
	r_output = svd_comp.rows_interpretable_output
	
	print "the energy captured with "+str(disp_k)+" concepts is "+str(energy_captured)+" %"
	
	#write the result
	print "writing SVD result for user "+str(user_id)+"..."
	JsonLogsFileWriter.write(r_output, file_name)
	
	
	
	
	
		
	
	
	