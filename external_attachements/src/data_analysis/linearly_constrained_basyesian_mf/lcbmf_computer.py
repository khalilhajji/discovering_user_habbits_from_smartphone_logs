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
from numpy_utils import Numpy
import math
import numpy as np
from datetime import datetime, timedelta
import scipy.io
import shutil
import subprocess




'''
LCBMFComputer stands for Linearly Constrained Bayesian Matrix Factorization.

It is a factorization matrix method that enable the user to specify constrains (linear constrains) on the resulted factor matrices desired.

Given a matrix X of size (m,n) and a dimensionality reduction parameter k, it finds two matrices A (m*k)and B(n*j) such that:
	- |X- A.B| <= sigma where sigma is very small
	- the elements of A (lets call them ai) verify the linear constrains indicated : coef1*ai-biais1 = 0 and coef2*ai-biais2>=0
	- the elements of B (lets call them bj) verify the linear constrains indicated : coef3*bj-biais3 = 0 and coef4*bj-biais4>=0
'''
class LCBMFComputer (object):
	temp_dir = "/speech/dbwork/mul/students/dehajjik/tmp_matrix_data/"
	x_matrix_mlab_name = "x_mat"
	a_constrains_mlab_name = "a_cons"
	b_constrains_mlab_name = "b_cons"
	
	a_matrix_mlab_name = "a_mat"
	b_matrix_mlab_name = "b_mat"
	
	mlab_ext = ".mat"
	
	equality_key="eq" 
	inequality_key="ineq"
	coefs_key="coef"
	biais_key="biais"
	
	mlab_lcbmf_dir_path = "/home/dehajjik/workspace/src_mlab/lcbmf/"
	
	shell_script_path = "/home/dehajjik/workspace/src/data_analysis/linearly_constrained_basyesian_mf/launch_mlab_lcbmf.sh"
	
	#the matlab function takes as input arguments path_to_matrix, path_to_a_constrains, path_to_b_constrains
	mlab_lcbmf_function_name = "compute_lcbmf"
	
	
	
	k_label = "k"
	time_dimention = 1
	feature_dimention = 0
	
	feature_display_size = 20
	
	'''
	possible values for:
		pretransformation_name : {"none" ,"idf", "ldc","idc","idf3", None}
		a_constrains_name : { "[0,1]", None}
		b_constrains_name : {"positive, sum=1", None}
	'''
	def __init__(self, matrix, pretransformation_name, a_constrains_name, b_constrains_name, k):
		self.x_matrix_data = matrix
		
		
		#initialize the name of the different transformations and constranis for the lcbmf
		self.pretransformation_name = pretransformation_name
		self.a_constrains_name = a_constrains_name
		self.b_constrains_name = b_constrains_name
		
		
		self.k = 5
		
		if k!= None:
			self.k = k
		
		
		'''
		The constrains of a is a dict that contains the 4 different keys representing the 4 different constrains to specify:
			-coefs for the equality of a
			-biais for the equality of a
			-coefs for the inequality of a
			-biais for the inequality of a
		'''
		self.a_constrains = {LCBMFComputer.equality_key+LCBMFComputer.coefs_key  :   [],
							LCBMFComputer.equality_key+LCBMFComputer.biais_key   :   [],
							LCBMFComputer.inequality_key+LCBMFComputer.coefs_key   :   [],
							LCBMFComputer.inequality_key+LCBMFComputer.biais_key   :   []
							}
		
		
		'''
		Same for b constrains
		'''
		self.b_constrains = {LCBMFComputer.equality_key+LCBMFComputer.coefs_key  :   [],
							LCBMFComputer.equality_key+LCBMFComputer.biais_key   :   [],
							LCBMFComputer.inequality_key+LCBMFComputer.coefs_key   :   [],
							LCBMFComputer.inequality_key+LCBMFComputer.biais_key   :   []
							}
		
		self.a_matrix = None
		self.b_matrix = None
		
		self.rows_interpretable_output = {}
		
		
	def compute(self):
		#make transformation if needed
		[transformed_matrix, transformation_scores_by_feature] = self._apply_pretransformation(self.x_matrix_data, self.pretransformation_name)
		
		#define the constrains
		self._define_constrains(self.a_constrains_name, self.b_constrains_name)
		
		
		#defining the paths of the different elements
		x_mat_path = LCBMFComputer.temp_dir+LCBMFComputer.x_matrix_mlab_name+LCBMFComputer.mlab_ext
		a_cons_path = LCBMFComputer.temp_dir+LCBMFComputer.a_constrains_mlab_name+LCBMFComputer.mlab_ext
		b_cons_path = LCBMFComputer.temp_dir+LCBMFComputer.b_constrains_mlab_name+LCBMFComputer.mlab_ext
		a_mat_path= LCBMFComputer.temp_dir+LCBMFComputer.a_matrix_mlab_name+LCBMFComputer.mlab_ext
		b_mat_path = LCBMFComputer.temp_dir+LCBMFComputer.b_matrix_mlab_name+LCBMFComputer.mlab_ext
		
		#write the matrix in the temp dir with a matlab extention
		self._create_dir(LCBMFComputer.temp_dir)
		self._write_in_mlab_format({LCBMFComputer.x_matrix_mlab_name:transformed_matrix}, x_mat_path)
		self._write_in_mlab_format(self.a_constrains, a_cons_path)
		self._write_in_mlab_format(self.b_constrains, b_cons_path)
		
		
		#execute the matlab code
		subprocess.call([LCBMFComputer.shell_script_path, LCBMFComputer.mlab_lcbmf_dir_path,x_mat_path, LCBMFComputer.x_matrix_mlab_name, a_cons_path, b_cons_path, LCBMFComputer.equality_key, 
						LCBMFComputer.inequality_key, LCBMFComputer.coefs_key, LCBMFComputer.biais_key, str(self.k), a_mat_path, b_mat_path])
		
		#read the results given by matlab from the temp dir
		
		self.a_matrix = self._load_mlab_format_unique_var(a_mat_path)
		self.b_matrix = self._load_mlab_format_unique_var(b_mat_path)
		
	
		
		#rempve the temp dir
		self._remove_dir(LCBMFComputer.temp_dir)
		
		return [self.a_matrix, self.b_matrix]
		
		
	def _apply_pretransformation(self, matrix, pretransformation_name):
		transformed_trainset = np.copy(matrix)
		
		
		if pretransformation_name == "none" or pretransformation_name == None:
			#initialize the transformation scores to an array of the size of the number of features and containing all ones. This is equivalent to not having made any transformation
			transformation_scores_by_feature = np.ones(np.shape(matrix)[LCBMFComputer.feature_dimention])
		
		elif pretransformation_name == "idf":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idf_matrix_transformation(matrix, LCBMFComputer.time_dimention, do_laplace_smoothing)
		
		elif pretransformation_name == "ldc":
			[transformed_trainset, transformation_scores_by_feature] = Numpy.ldc_matrix_transformation(matrix, LCBMFComputer.time_dimention)
		
		elif pretransformation_name == "idc":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idc_matrix_transformation(matrix, LCBMFComputer.time_dimention, do_laplace_smoothing)
		
		elif pretransformation_name == "idf3":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idf3_matrix_transformation(matrix, LCBMFComputer.time_dimention, do_laplace_smoothing)
		
		else:
			raise Exception("WRONG TRANSFORMATION EXCEPTION : the transformation "+pretransformation_name+" do not exist")
			
		return [transformed_trainset, transformation_scores_by_feature]
	

	'''
	functions dealing with the constrains of a and b are defined below
	'''
	def _define_constrains(self, a_constrains_name, b_constrains_name):
		self._define_a_constrains(a_constrains_name)
		self._define_b_constrains(b_constrains_name)

		
	def _define_a_constrains(self, constrains_name):
		if constrains_name == "[0,1]" or constrains_name == None:
			self._a_between_zero_and_one()
		else:
			raise Exception("WRONG TRANSFORMATION EXCEPTION : the constrains "+constrains_name+" do not exist")
	
	def _a_between_zero_and_one(self):
		'''
		for a_constrains we want the following:
			0<=ai<=1 this is equvalent to:
				ai>=0 and ----------------------> identify_matrix(k)*[a1,...,ak]T - [0,.....0]T >= [0,....,0]T 
				-ai+1>=1  ----------------------> -identify_matrix(k)*[a1,...,ak]T - [-1,.....,-1]T >= [0,....,0]T
		
		Note here that each ai represents a topic (a column) -> ai goes from 0 to k-1
		'''
		a_ineq_coef = np.concatenate((np.identity(self.k),-np.identity(self.k)),0)
		a_ineq_biais = np.concatenate((np.zeros((self.k,1)), -np.ones((self.k,1))),0)
		
		#no equalities for a
		self.a_constrains = {LCBMFComputer.equality_key+LCBMFComputer.coefs_key  :   [],
							LCBMFComputer.equality_key+LCBMFComputer.biais_key   :   [],
							LCBMFComputer.inequality_key+LCBMFComputer.coefs_key   :   a_ineq_coef,
							LCBMFComputer.inequality_key+LCBMFComputer.biais_key   :   a_ineq_biais
							}
							
	def _define_b_constrains(self, constrains_name):
		if constrains_name == "positive, sum=1" or constrains_name == None:
			self._b_positive_sum_to_one()
		else:
			raise Exception("WRONG TRANSFORMATION EXCEPTION : the constrains "+constrains_name+" do not exist")
	
	def _b_positive_sum_to_one(self):
		'''
		for b_constrains we want the following:
		1- bi >= 0-----------------------------------> identify_matrix(k)*[b1,...,bk]T - [0,.....0]T >= [0,....,0]T
		2- Sum bi  = 1 ------------------------------> [1,.......,1] * [b1,...,bk]T -1 = 0
		'''
		b_ineq_coef = np.identity(self.k)
		b_ineq_biais = np.zeros((self.k,1))
		
		b_eq_coef = np.ones((1,self.k))
		b_eq_biais = 1
		
		self.b_constrains = {LCBMFComputer.equality_key+LCBMFComputer.coefs_key  :   b_eq_coef,
							LCBMFComputer.equality_key+LCBMFComputer.biais_key   :   b_eq_biais,
							LCBMFComputer.inequality_key+LCBMFComputer.coefs_key   :   b_ineq_coef,
							LCBMFComputer.inequality_key+LCBMFComputer.biais_key   :   b_ineq_biais
							}

	'''
	Call this method to construct a humanely readable clusters result. They are represented as a dictionary stored in the class attribute rows_interpretable_output
	from the realization and the id_info returns the label of this realization 
	nb_features_display: for each concept the number of features to display
	'''
	def construct_rows_interpretable_output(self, row_labels, nb_features_display):
		#built the interpretable output as a dictionary
		self.rows_interpretable_output[LCBMFComputer.k_label] = {}
		nb_concepts = self.k
		u = self.a_matrix
		
		b_sums = np.sum(self.b_matrix,1)
		b_norm = b_sums/(np.sum(b_sums,0)*1.0)
		
		for k in range(0, nb_concepts):
			kth_key = str(k)+" : "+str(b_norm[k])
			self.rows_interpretable_output[self.k_label][kth_key]={}
			kth_output={}
			kth_vector = u[:,k]
			
			nb_rows = None
			if np.size(kth_vector) == len(row_labels):
				nb_rows = np.size(kth_vector)
			else:
				raise Exception("NON MATCHING LENGTHS EXCEPTIONS: the columns vector has size "+size(kth_vector)+" whereas the corresponding number of labels is "+len(row_labels))
				
			
			for m in range(0, nb_rows):
				kth_output[row_labels[m]] = kth_vector[m]
				
			
			kth_output = collections.OrderedDict(sorted(kth_output.items(), key=lambda item: abs(item[1]), reverse= True)[0:nb_features_display]) 
			self.rows_interpretable_output[self.k_label][kth_key] = kth_output
			
			self.rows_interpretable_output[self.k_label] = collections.OrderedDict(sorted(self.rows_interpretable_output[self.k_label].items(), key=lambda item: int(item[0].split(" : ")[0]))) 
			
	'''
	I/O functions defined below
	'''
	def _write_in_mlab_format(self, numpy_object, key, path):
		scipy.io.savemat(path, {key:numpy_object})
		
	def _write_in_mlab_format(self, var_object_dict, path):
		scipy.io.savemat(path, var_object_dict)
	
	def _load_mlab_format_unique_var(self, path):
		#environment_var are variables added automatically by matlab so we filter them
		environment_var = ['__version__', '__header__', '__globals__']
		dict = scipy.io.loadmat(path)
		for key in dict.keys():
			if key not in environment_var:
				return dict[key]
	
	
	def _remove_dir(self, path):
		shutil.rmtree(path)
		
	def _create_dir(self, dir_path):
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)