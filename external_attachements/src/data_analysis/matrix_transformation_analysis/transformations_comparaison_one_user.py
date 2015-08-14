#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from json_utils import JsonUtils
from numpy_utils import Numpy
from matrix_data_utils import *
from logs_file_writer import LogsFileWriter
from plot_lib_utils import PlotlibDrawer
'''

'''
disp_k = 5
disp_m = 20
do_laplace_smoothing = True
time_dimention = 1


labels_importance = {}
labels_importance_derivative = {}
labels_importance_rank = {}
transformation_vectors = {}
rows_labels = None
file_name = None
def transformations_comparaison_one_user(user_id):
	global file_name
	global rows_labels
	global labels_importance
	global labels_importance_derivative
	global labels_importance_rank
	global transformation_vectors
	
	labels_importance = {}
	labels_importance_derivative = {}
	labels_importance_rank = {}
	transformation_vectors = {}
	rows_labels = None
	file_name = None
	file_name = "transformations_comparaison_"+str(user_id)
	print "loading matrix user "+str(user_id)+"..."
	data_matrix = MDataExtractor.load_matrix(user_id)
	
	rows_labels =  MDataExtractor.load_labels_vector(user_id)
	columns_labels = MDataExtractor.load_time_vector(user_id)
	importance_scores = MDataExtractor.load_importance_scores(user_id)
	
	

	
	add_transformation(data_matrix, "presence_count")
	add_transformation((data_matrix*100/(np.size(data_matrix,time_dimention)*1.0)), "presence_percentage")
		
	idf_matrix = Numpy.idf_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	add_transformation(idf_matrix, "idf_score")
	
	
	'''idf2_matrix = Numpy.idf2_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	add_transformation(idf2_matrix, "idf2_score")'''
	
	'''idf10_matrix = Numpy.idflog10_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	add_transformation(idf10_matrix, "idflog10_score")'''
	
	idf3_matrix = Numpy.idf3_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	add_transformation(idf3_matrix, "idf3_score")
	
	ldc_matrix = Numpy.ldc_matrix_transformation(data_matrix, time_dimention)
	add_transformation(ldc_matrix, "ldc_score")
		
	idc_matrix = Numpy.idc_matrix_transformation(data_matrix, time_dimention, do_laplace_smoothing)
	add_transformation(idc_matrix, "idc_score")
	
	
	
	
	compare("presence_count", user_id)

	
	
def add_transformation(matrix, transformation_name):
	global transformation_vectors
	sum_vector = matrix.sum(time_dimention)
	rank_vector = Numpy.ranks(sum_vector, reverse = True)
	
	transformation_vectors[transformation_name]={}
	transformation_vectors[transformation_name][0] = sum_vector
	transformation_vectors[transformation_name][1] = rank_vector
	#transformation_vectors[transformation_name][2] = np.diff(sum_vector, 1)
	
def compare(reference_transformation, user_id):
	global labels_importance
	global labels_importance_rank
	#global labels_importance_derivative
	index = 0
	transformations = transformation_vectors.keys()
	for label in rows_labels:
		labels_importance[label] = {}
		labels_importance_rank[label] = {}
		for transformation in transformations:
			labels_importance[label][transformation]=transformation_vectors[transformation][0][index]
			labels_importance_rank[label][transformation]= transformation_vectors[transformation][1][index]
			#labels_importance_derivative[label][transformation]= transformation_vectors[transformation][2][index]
		
		index +=1
		
		
	#sort the dictionaries per presence rate. The most frequent feature at the biginning
	labels_importance = collections.OrderedDict(sorted(labels_importance.items(), key=lambda x: x[1][reference_transformation], reverse = True))
	#labels_importance_derivative = collections.OrderedDict(sorted(labels_importance_derivative.items(), key=lambda x: x[1][reference_transformation], reverse = True))
	labels_importance_rank = collections.OrderedDict(sorted(labels_importance_rank.items(), key=lambda x: x[1][reference_transformation]))
	
	
	print JsonUtils.dict_as_json_str(labels_importance)
	
	print JsonUtils.dict_as_json_str(labels_importance_rank)
	#print np.shape(data_matrix)
	
	#write the dictionaries into files
	out = LogsFileWriter.open(file_name)
	LogsFileWriter.write(JsonUtils.dict_as_json_str(labels_importance),out)
	LogsFileWriter.write(JsonUtils.dict_as_json_str(labels_importance_rank),out)
	LogsFileWriter.close(out)
	
	
	#plot the records importance vs different transformation scores
	importances_list = []
	importances_legends = []
	ranks_list = []
	ranks_legends = []
	importances_derivatives_list = []
	importances_derivatives_legends = []
	for transformation in transformations:
		importance_list = [importance[transformation] for importance in labels_importance.values()]
		importances_list.append(importance_list)
		importances_legends.append(transformation)
		
		rank_list = [rank[transformation] for rank in labels_importance_rank.values()]
		ranks_list.append(rank_list)
		ranks_legends.append(transformation)
		
		importance_derivative_list = np.diff(np.asarray(importance_list), 1).tolist()
		importances_derivatives_list.append(importance_derivative_list)
		importances_derivatives_legends.append(transformation)
		
		
	importances_derivatives_list.append([0]*len(importances_derivatives_list[0]))
	importances_derivatives_legends.append("y=0")
	PlotlibDrawer.plot_1(labels_importance.keys(), [percentage["presence_percentage"] for percentage in labels_importance.values()], "features rank", "% records", "presence rate of the features in the records", 10)
	PlotlibDrawer.plot_2(labels_importance.keys(), importances_list, importances_legends, "features rank", "features scores", "comparison of different transformation scores "+str(user_id), 11)
	PlotlibDrawer.plot_2(labels_importance_rank.keys(), ranks_list, ranks_legends, "features initial rank", "features rank after transformation", "comparison of different transformation ranks "+str(user_id), 11)
	PlotlibDrawer.plot_2(labels_importance.keys(), importances_derivatives_list, importances_derivatives_legends, "features initial rank", "features scores derivative", "comparison of different transformation scores derivative "+str(user_id), 11)
	
		
	
	
	
		
	
	
	