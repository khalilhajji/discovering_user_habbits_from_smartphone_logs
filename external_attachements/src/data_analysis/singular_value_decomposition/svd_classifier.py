import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/data_analysis/common")
from classifier import MClassifier
import numpy as np
import numpy.ma as ma
import numpy.linalg as linalg
from numpy_utils import Numpy



class SVDClassifier (MClassifier):
	#the number of singular values to take into account for the truncated SVD
	
	time_dimention = 1
	feature_dimention = 0
	def __init__(self, pretransformation_name, k):
		MClassifier.__init__(self)
		
		self.pretransformation = pretransformation_name
		
		#those are the scores of the pretransformation applied in the train set by feature (ex: idf transformation)
		self.transformation_scores_by_feature = None
		
		#those represents the resulting matrixes from the decompositon X_hat = U.D.V with ||X-X_hat|| small
		self.u_matrix = None
		self.s_vector = None
		self.v_matrix = None
		
		self.k = 20
		if k!= None:
			self.k = k
		
			
	
	
	
	'''
	train the classifier on the given train matrix
	train_data_matrix: numpy  2-dimentional matrix
	'''
	def train(self, train_data_matrix):
		
		#transform of the matrix and save the transformations applied by feature
		[transformed_trainset, self.transformation_scores_by_feature] = self.apply_pretransformation(train_data_matrix, self.pretransformation)
		
		#compute the u, s ,v matrixes on the train set
		[self.u_matrix, self.s_vector, self.v_matrix] = linalg.svd(transformed_trainset, full_matrices=False, compute_uv=True)
		
		#truncate k 
		k = self.k
		self.u_matrix = self.u_matrix[:,0:k]
		self.s_vector = self.s_vector[0:k]
		self.v_matrix = self.v_matrix[0:k, :]
		
	
	def apply_pretransformation(self, matrix, pretransformation_name):
		transformed_trainset = np.copy(matrix)
		
		
		if pretransformation_name == "none":
			#initialize the transformation scores to an array of the size of the number of features and containing all ones. This is equivalent to not having made any transformation
			transformation_scores_by_feature = np.ones(np.shape(matrix)[SVDClassifier.feature_dimention])
		
		elif pretransformation_name == "idf":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idf_matrix_transformation(matrix, SVDClassifier.time_dimention, do_laplace_smoothing)
		
		elif pretransformation_name == "ldc":
			[transformed_trainset, transformation_scores_by_feature] = Numpy.ldc_matrix_transformation(matrix, SVDClassifier.time_dimention)
		
		elif pretransformation_name == "idc":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idc_matrix_transformation(matrix, SVDClassifier.time_dimention, do_laplace_smoothing)
		
		elif pretransformation_name == "idf3":
			do_laplace_smoothing = True
			[transformed_trainset, transformation_scores_by_feature] = Numpy.idf3_matrix_transformation(matrix, SVDClassifier.time_dimention, do_laplace_smoothing)
		
		else:
			raise Exception("WRONG TRANSFORMATION EXCEPTION : the transformation "+pretransformation_name+" do not exist")
			
		return [transformed_trainset, transformation_scores_by_feature]
	'''
	classify the test set elements
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is list array that contains the scores corresponding to the decided features
	'''
	def classify_with_no_regroup(self, test_data_matrix, ids_features_to_classify):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		x_test_data_matrix_hat = self.fill_gaps_in_testset(test_data_matrix, ids_features_to_classify)
		
		#now we have a matrix where the higher the value of a feature in a record is, the more this feature is 'important' in that record.
		#Thus from the list of the features to predict, the one that is selected in each record is the one that has the higher value.
		winner_ids = []
		winner_scores = []
		#for each record, take the feature corresponding to the maximal value
		for i in range(0, np.shape(x_test_data_matrix_hat)[SVDClassifier.time_dimention]):
			record = x_test_data_matrix_hat[:,i]
			winner_score = np.amax(record)
			winner_id = np.argmax(record)
			if winner_id not in ids_features_to_classify:
				winner_id = SVDClassifier.unknown_feature_id
			
			winner_ids.append(winner_id)
			winner_scores.append(winner_score)
		
		return [winner_ids, winner_scores]
	
	
	'''
	classify the test set elements and then regroup the classified elements according to their group to decide a common class for them
	test_data_matrix: 2-dimentional numpy array where the columns represents the vectors to classify
	ids_features_to_classify: the ids of the hidden features that needs to be classified
	groups: [[id1_groupe1,...,id_n1_groupe1],...,[id_1_groupem, ..., id_nm_groupem]]
	return [ids , scores] where:
	ids: is a list that contains the id of the feature decided by the classifier for each vector element
	scores: is a list array that contains the scores corresponding to the decided features
	'''	
	def regroup_and_classify(self, test_data_matrix, ids_features_to_classify, groups):
		#get a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
		x_test_data_matrix_hat = self.fill_gaps_in_testset(test_data_matrix, ids_features_to_classify)
		
		#now we have a matrix where the higher the value of a feature in a record is, the more this feature is 'important' in that record.
		#We decide that summing the values of different records belonging to the same group indicates the importance of the features in that group.
		#Thus, the classified feature for one group of records is the one that has the biggest sum
		winner_ids = []
		winner_scores = []
		#for each group, take the feature corresponding to the maximal value of the sum of the records belonging to the group
		for group in groups:
			group_record = x_test_data_matrix_hat[: , group].sum(SVDClassifier.time_dimention)
			winner_score = np.amax(group_record)
			winner_id = np.argmax(group_record)
			
			if winner_id not in ids_features_to_classify:
				winner_id = SVDClassifier.unknown_feature_id
				
			winner_ids.append(winner_id)
			winner_scores.append(winner_score)
		
		
		return [winner_ids, winner_scores]
		
	'''
	input: testdata , features_to_classify
	output: a matrix of the same size than the test matrix that contains the estimated values for the features to classify, and 0 otherwise else
	'''	
	def fill_gaps_in_testset(self, test_data_matrix, ids_features_to_classify):
		if self.u_matrix == None:
			raise Exception("NON TRAINED CLASSIFIER EXCEPTION: the classifier needs to be trained before if is able to make classifications")
			
		#apply the same transformation to the test test than applied for the train set
		transformed_testset = self.transformation_scores_by_feature.reshape(np.size(self.transformation_scores_by_feature),1)*test_data_matrix
		
		#project the transformed matrix into the SVD space  Xtest_Hat = Uk.Sk.(invSk.invUk.Xtest). Xtest_hat represents the approximated matrix of the X_test taking into account
		#the k most important dimensions. Note that invUk = Uk_transposed 
		s_matrix = np.diag(self.s_vector)
		u_matrix_inversed = np.transpose(self.u_matrix)
		v_test_matrix = np.dot(linalg.inv(s_matrix), np.dot(u_matrix_inversed,transformed_testset))
		x_transformedtest_hat = np.dot(np.dot(self.u_matrix, s_matrix),v_test_matrix)
		
		#do the inverse transformation to recover the original state of the test matrix (approximated)
		x_test_data_matrix_hat = x_transformedtest_hat / self.transformation_scores_by_feature.reshape(np.size(self.transformation_scores_by_feature),1)
		
		#keep only the rows corresponding to the features to predict and put all the others to 0
		mask = np.zeros(np.shape(x_test_data_matrix_hat))
		mask[ids_features_to_classify,:] = 1
		x_test_data_matrix_hat = x_test_data_matrix_hat*mask
		
		return x_test_data_matrix_hat
		