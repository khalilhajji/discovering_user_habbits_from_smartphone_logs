'''
class that contains some utility functions about the numpy arrays
'''
#contains some utils functions that manipulate numpy objects
#!/usr/bin/env python
import numpy as np
from pprint import *
import math

class Numpy():
	#return a pretty string representation of a numpy object
	@staticmethod
	def str(np_object):
		np.set_printoptions(precision=2, linewidth= 150, suppress=True)
		return pformat(np_object)
		
	
	'''
	do the inverse document frequency (google it if needed) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idf: multiply each feature f of the matrix by log(number_of_realizations/number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f do not appear in any realization, then its idf will be log(#realizations/0) which will give Nan. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((number_of_realizations+1)/(number_of_realizations_containing_f+1)). Note that for big number_of_realizations the impact for the +1 is not big
	'''
	@staticmethod
	def idf_matrix_transformation(matrix, dimention, do_laplace_smoothing):
		nb_realizations_total = np.size(matrix,dimention)
		print "nb_total realizations for idf is "+str(nb_realizations_total)
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		if do_laplace_smoothing:
			#add one realization for each of the features that do not appear in all documents to avoid the 0
			nb_realizations_by_feature = (nb_realizations_by_feature + 1)
			nb_realizations_total += 1
		
		
		#vector where dimention i represents the idf score for the feature i
		idf_by_feature = np.log(nb_realizations_total/nb_realizations_by_feature)
		
		
		
		#multipy each entry of the matrix by its idf coefficient
		idf_matrix = idf_by_feature.reshape(np.size(idf_by_feature),1)*matrix
		
		return [idf_matrix, idf_by_feature]
		
	'''
	do the inverse document frequency (google it if needed) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idf: multiply each feature f of the matrix by log(number_of_realizations/number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f do not appear in any realization, then its idf will be log(#realizations/0) which will give Nan. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((number_of_realizations+1)/(number_of_realizations_containing_f+1)). Note that for big number_of_realizations the impact for the +1 is not big
	'''
	@staticmethod
	def idflog10_matrix_transformation(matrix, dimention, do_laplace_smoothing):
		nb_realizations_total = np.size(matrix,dimention)
		print "nb_total realizations for idf is "+str(nb_realizations_total)
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		if do_laplace_smoothing:
			#add one realization for each of the features that do not appear in all documents to avoid the 0
			nb_realizations_by_feature = (nb_realizations_by_feature + 1)
			nb_realizations_total += 1
		
		
		#vector where dimention i represents the idf score for the feature i
		idf_by_feature = np.log10(nb_realizations_total/nb_realizations_by_feature)
	
		
		
		#multipy each entry of the matrix by its idf coefficient
		idf_matrix = idf_by_feature.reshape(np.size(idf_by_feature),1)*matrix
		
		return [idf_matrix,idf_by_feature]
		
		
	'''
	do the inverse document frequency (google it if needed) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idf: multiply each feature f of the matrix by log(max_number_of_realizations_containing_the_same_feature/number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f do not appear in any realization, then its idf will be log(#realizations/0) which will give Nan. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((max_number_of_realizations_containing_the_same_feature+1)/(number_of_realizations_containing_f+1)). Note that for big max_number_of_realizations_containing_the_same_feature the impact for the +1 is not big
	'''
	@staticmethod
	def idf2_matrix_transformation(matrix, dimention, do_laplace_smoothing):
		
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		max_nb_realizations_total = np.max(nb_realizations_by_feature)
		print "nb_total realizations for idf is "+str(max_nb_realizations_total)
		
		if do_laplace_smoothing:
			#add one realization for each of the features that do not appear in all documents to avoid the 0
			nb_realizations_by_feature = (nb_realizations_by_feature + 1)
			max_nb_realizations_total +=1
		
		
		#vector where dimention i represents the idf score for the feature i
		idf_by_feature = np.log(max_nb_realizations_total/nb_realizations_by_feature)
	
		
		
		#multipy each entry of the matrix by its idf coefficient
		idf_matrix = idf_by_feature.reshape(np.size(idf_by_feature),1)*matrix
		
		return [idf_matrix,idf_by_feature]
		
		
	'''
	do the inverse document frequency (google it if needed) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idf: multiply each feature f of the matrix by log(number_of_realizations/number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f do not appear in any realization, then its idf will be log(#realizations/0) which will give Nan. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((number_of_realizations+1)/(number_of_realizations_containing_f+1)). Note that for big number_of_realizations the impact for the +1 is not big
	'''
	@staticmethod
	def idf3_matrix_transformation(matrix, dimention, do_laplace_smoothing):
		nb_realizations_total = np.size(matrix,dimention)*1.5
		print "nb_total realizations for idf is "+str(nb_realizations_total)
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		if do_laplace_smoothing:
			#add one realization for each of the features that do not appear in all documents to avoid the 0
			nb_realizations_by_feature = (nb_realizations_by_feature + 1)
			nb_realizations_total += 1
		
		
		#vector where dimention i represents the idf score for the feature i
		idf_by_feature = np.log(nb_realizations_total/nb_realizations_by_feature)

		
		
		#multipy each entry of the matrix by its idf coefficient
		idf_matrix = idf_by_feature.reshape(np.size(idf_by_feature),1)*matrix
		
		return [idf_matrix, idf_by_feature]
		
		
	'''
	do the linear document count (google it if needed) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idf: multiply each feature f of the matrix by log(number_of_realizations/number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f do not appear in any realization, then its idf will be log(#realizations/0) which will give Nan. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((number_of_realizations+1)/(number_of_realizations_containing_f+1)). Note that for big number_of_realizations the impact for the +1 is not big
	'''
	@staticmethod
	def ldc_matrix_transformation(matrix, dimention):
		nb_realizations_total = np.size(matrix,dimention)
		a = - (math.log(nb_realizations_total))/(nb_realizations_total-1)
		b = (nb_realizations_total/(nb_realizations_total-1))*math.log(nb_realizations_total)
		print "nb_total realizations for idf is "+str(nb_realizations_total)
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		
		#add one realization for each of the features that do not appear in all documents to avoid the 0
		#nb_realizations_by_feature = (nb_realizations_by_feature + 1)
		#nb_realizations_total += 1
		
		
		#vector where dimention i represents the idf score for the feature i
		ldc_by_feature = (a*nb_realizations_by_feature)+b

		
		
		#multipy each entry of the matrix by its idf coefficient
		ldc_matrix = ldc_by_feature.reshape(np.size(ldc_by_feature),1)*matrix
		
		return [ldc_matrix,ldc_by_feature]
		
	
	'''
	do the inverse document count (softer than the idf) transformation in the given matrix and return a new transformed matrix. 
	the dimention indicates the dimention that represents the documents.
	
	idc: multiply each feature f of the matrix by log(number_of_realizations-number_of_realizations_containing_f) -> realizations very frequent in many documents will take less importance
	ex: if a feature f appears in all the realizations except one its idt score will be log(1)=0 
	
	laplace_smoothing: if a feature f appears in all the realizations, then its idf will be log(#realizations-#realizations) which will give -infinity. To avoid that, laplace_smoothing will compute the 
	idf by the following :  log((number_of_realizations+1)-number_of_realizations_containing_f). Note that for big number_of_realizations the impact for the +1 is not big
	'''
	@staticmethod
	def idc_matrix_transformation(matrix, dimention, do_laplace_smoothing):
		nb_realizations_total = np.size(matrix,dimention)
		
		#vector where dimention i represents the number of realizations containing the feature i
		nb_realizations_by_feature = (matrix>0).sum(dimention) * 1.0
		
		if do_laplace_smoothing:
			#add one realization for each feature to avoid the 0
			nb_realizations_total = nb_realizations_total + 1
		
		#vector where dimention i represents the idf score for the feature i
		idc_by_feature = np.log(nb_realizations_total-nb_realizations_by_feature)
		
		#multipy each entry of the matrix by its idf coefficient
		idc_matrix = idc_by_feature.reshape(np.size(idc_by_feature),1)*matrix
		
		return [idc_matrix,idc_by_feature]
	
	'''
	do the term importance transformation in the given matrix and return a new transformed matrix. 
	multiplies each occurrence by the importance of this corresponding term
	'''
	@staticmethod
	def ti_matrix_transformation(matrix, term_importance_vector):
		ti_matrix = term_importance_vector.reshape(np.size(term_importance_vector),1)*matrix
		
		return ti_matrix
		
		
	@staticmethod	
	def nti_matrix_transformation(matrix, term_importance_vector):
		print term_importance_vector
		ti_matrix = Numpy.ti_matrix_transformation(matrix,  term_importance_vector)
		max_term_score_by_record = ti_matrix.max(0)*1.0
		nti_matrix = ti_matrix / max_term_score_by_record.reshape(1,np.size(max_term_score_by_record))
		
		return nti_matrix
		
	'''
	Take as input a vector an returns a vector containing the rank position of each element (increasing sorting)
	when reverse = true then the sorting is done deacreasing
	
	ex: input [4,3,7,1] -> output [2,1,3,0]
	'''	
	@staticmethod	
	def ranks(vector, reverse):
		arg_ranks = vector.argsort()
		if reverse:
			arg_ranks = arg_ranks[::-1]
		ranks = np.empty(len(arg_ranks), int)
		ranks[arg_ranks]=np.arange(len(arg_ranks)) 
		
		return ranks
		
		