#-*- coding: utf-8 -*- 

"""
EXPECTATION MAXIMIZAZION IMPLEMENTATION FOR HIDDEN CLASS MODEL FOR MIXED DATE TYPES (HCM_MDT)
IMPLEMENTED BY KHALIL HAJJI in 07/2015
"""

import sys
import random as rnd
import gc
from scipy.special import gamma, gammaln, psi
from scipy.stats import *
from scipy import *
import numpy as np

class HcmMdt(object):
	hyper_parameter_llikelihood_converge_threshold = 1e-4
	"""
	P:  Dictionary [feature_id]: Array[nb_hclass, vocab_size] where each row is topic
	Pi: Array [nb_records, nb_hclass] that associates to each document the mix coeffs
		over topics
	rsp:  dictionary such as rsp[d][f][w]: array [nb_hclass, 1] with the rsp of each
		topic in generating word w in document d
	N:    Array [nb_records, nb_hclass] that associate to each topic and each document
		the estimation of number of realisations sampled from it
	data: dictionary data[doc_id][feature_id]:Array[values , 1] values of feature that appears in record
		ex [v1,v1,v2,...,v3]
	nb_hclass: number of hidden class required
	vocab_size: Array[nb_features] : the vocabulary size of each feature (1st cell corresponds to voc size of f1
                  2nd cell to voc size of f2,... Fth cell to voc size of fF)
	"""
	def __init__(self, data, nb_hclass, vocab_size):
		self.nb_records = len(data)
		self.nb_hclass = nb_hclass # nb of topics to find
		self.vocab_size = vocab_size # Vocabulary size
		self.nb_features = len(vocab_size)
    
		self.Pi = np.zeros((self.nb_records, self.nb_hclass))
		self.rsp = dict()
		self.data = data

		self.P = dict()
		for f in range(self.nb_features):
			self.P[f] = np.zeros((self.nb_hclass, self.vocab_size[f]))             # SPACE FOR PHI MATRIX WITH 0s

	def initialize(self):
		for r in self.data:
			self.rsp[r] = dict()
			for f in self.data[r]:
				self.rsp[r][f]=dict()
				for v in self.data[r][f]:
					self.rsp[r][f][v] = 0

		self.Pi = self.normalize_mat(np.random.rand(self.nb_records, self.nb_hclass))
		for f in range(self.nb_features):
			self.P[f]= self.normalize_mat(np.random.rand(self.nb_hclass, self.vocab_size[f]))

	def e_phase(self):
		"""E phase: evaluate the responsabilities using the current values of
		Pi and P"""
		for r in self.rsp:
			for f in self.rsp[r]:
				for v in self.rsp[r][f]:
					p = self.Pi[r,:]*self.P[f][:,v] # p[k] = p[z=k|w]
					self.rsp[r][f][v] = p/np.sum(p)

	def m_phase(self):
		"""Re-estimate the parameters Pi and P using the current responsabilities"""
		P = dict()
		for f in range(self.nb_features):
			P[f] = np.zeros(self.P[f].shape)
		# Compute the Expected number of words N_k per topic
		N = np.zeros(self.Pi.shape)
		for r in self.data:
			for f in self.data[r]:
				for v in self.data[r][f]:
					N[r,:] += (self.rsp[r][f][v]).transpose()
					P[f][:,v] += self.rsp[r][f][v]

		self.Pi = self.normalize_mat(N) # Update the mixture coefficients
		for f in range(self.nb_features):  # Update the topics
			self.P[f]= self.normalize_mat(P[f])


	def likelihood(self):
		"""Returns the log likelihood of the data given the model parameters"""
		ll = 0
		size = 0
		for r in self.data:
			for f in self.data[r]:
				for v in self.data[r][f]:
					ll += np.log(np.dot(self.Pi[r,:],self.P[f][:,v]))
					size+=1
		av_ll = ll/size
		return [ll, av_ll]

	def fit(self, max_iter):
		"""Run the EM algo for the mixture of multinomials. The algo converges as
		as soon as we reach the maximum number of iterations [max_iter] or if the
		change in likleihood is less than a given threshold [delta]"""

		convergence = False
		print "MM with {0} documents and {1} topics".format(self.nb_records, self.nb_hclass)
		print "Running EM, Max number of iterations: {0}".format(max_iter)
		self.initialize()
		ll = [self.likelihood()]
		while not convergence:
			print "Iter {0}, [likelihood, average likelihood] {1}".format(len(ll)-1, ll[-1])
			self.e_phase()
			self.m_phase()
			ll.append(self.likelihood())
			convergence = (len(ll) > max_iter) or (abs(ll[-1][0] - ll[-2][0])/abs(ll[-2][0]) < self.hyper_parameter_llikelihood_converge_threshold)
		print "Iter {0}, [likelihood, average likelihood] {1}".format(len(ll)-1, ll[-1])
		return np.exp(-ll[-1][1]) #Return the final perplexity


	def initialize_newr(self, new_data):
		new_rsp=dict()
		for r in new_data:
			new_rsp[r] = dict()
			for f in new_data[r]:
				new_rsp[r][f]=dict()
				for v in new_data[r][f]:
					new_rsp[r][f][v] = np.zeros((self.nb_hclass))

		new_Pi = self.normalize_mat(np.random.rand(len(new_data), self.nb_hclass))
		return [new_rsp, new_Pi]

	def e_phase_newr(self, new_rsp, new_Pi):
		"""E phase: evaluate the responsabilities using the trained values of
		P and the current Pi"""
		for r in new_rsp:
			for f in new_rsp[r]:
				for v in new_rsp[r][f]:
					p = new_Pi[r,:]*self.P[f][:,v] # p[k] = p[z=k|w]
					if not np.all([p==0]) : new_rsp[r][f][v] = p/np.sum(p)
		return new_rsp


	def m_phase_newr(self, new_data, new_rsp):
		"""Re-estimate the parameters Pi and P using the current responsabilities"""
		N = np.zeros((len(new_data), self.nb_hclass))
		for r in new_data:
			for f in new_data[r]:
				for v in new_data[r][f]:
					N[r,:] += (new_rsp[r][f][v]).transpose()
		new_Pi = self.normalize_mat(N) # Update the mixture coefficients
		return new_Pi

	def likelihood_newr(self, new_data, new_Pi):
		"""Returns the log likelihood of the data given the model parameters"""
		ll = 0
		size = 0
		for r in new_data:
			for f in new_data[r]:
				for v in new_data[r][f]:
					if not np.all([self.P[f][:,v]==0]): ll += np.log(np.dot(new_Pi[r,:],self.P[f][:,v]))
					size+=1
		av_ll = ll/size
		return [ll, av_ll]


	def fit_newrecords(self, new_data, max_iter):
		"""Run the EM algo for the mixture of multinomials. The algo converges as
		as soon as we reach the maximum number of iterations [max_iter] or if the
		change in likleihood is less than a given threshold [delta]"""

		convergence = False
		print "MM with {0} documents and {1} topics".format(self.nb_records, self.nb_hclass)
		print "Running EM, Max number of iterations: {0}".format(max_iter)
		[new_rsp, new_Pi] = self.initialize_newr(new_data)
		ll = [self.likelihood_newr(new_data, new_Pi)]
		while not convergence:
			print "Iter {0}, [likelihood, average likelihood] {1}".format(len(ll)-1, ll[-1])
			new_resp = self.e_phase_newr(new_rsp, new_Pi)
			new_Pi = self.m_phase_newr(new_data, new_rsp)
			ll.append(self.likelihood_newr(new_data, new_Pi))
			convergence = (len(ll) > max_iter) or (abs(ll[-1][0] - ll[-2][0])/abs(ll[-2][0]) < self.hyper_parameter_llikelihood_converge_threshold)
		print "Iter {0}, [likelihood, average likelihood] {1}".format(len(ll)-1, ll[-1])
		print "PERPLEXITY "+str(np.exp(-ll[-1][1]))
		return [new_Pi, np.exp(-ll[-1][1])] #Return the final perplexity
		
	def perplexity_newrecords(self, new_data): #PERPLEXITY NEW RECORDS exp(-(sum(pr(v_new|original_data))/size_new))	
		pr_vnew = dict()
		for f in range(self.nb_features): #PR(V|ORIGINAL_DATA)=Exp[PR(V|R)]
			pr_vnew[f] = np.sum(np.dot(self.Pi,self.P[f]),0)/self.nb_records
        
		ll=0; size = 0;
		for r in new_data: #LOG_LIKELIHOOD(NEW_DATA) = SUM(LOG(PR(V_new|ORIGINAL DATA)))
			for f in new_data[r]:
				pr_v = pr_vnew[f][new_data[r][f]]
				ll+= np.sum(np.log(pr_v[pr_v>0])); size+=len(new_data[r][f]) #Here we ignore the values giving prob 0
		perplexity = np.exp(-ll/size)										 #(i.e never seen words in the original data)
		return perplexity												     #TO NOT HAVE INFINITE PERPLEXITY


	def normalize_mat(self, M):
		"""
		This function normalizes the matrix M so the sum of its elements along
		each row is 1

		Arguments:
		- `M`: numpy array
		"""
		if len(M.shape) ==2:
			M = 1.0*np.array(M)
			s =  np.sum(M,axis=1)
			index = np.nonzero(s)[0]
			s = s[index]
			s = s.reshape(s.size,1,order='F')
			M[index,:] = M[index,:] / np.tile(s,(1,M.shape[1]))
			return M
		else:
			if len(M.shape)==1:
				return M/np.sum(M)


#for testing
if __name__ == "__main__":
	print("GIBBS SAMPLING FOR GENERATIVE HIDDEN CLASS MODELLING FOR MIXED DATE TYPES (GHCM_MDT) INFERENCE.")
	data={0: {0:[0,0,1,4,5],
              1:[0,1,2,3]
              },
          1:  {0:[0,3,2],
               2:[6,6,6]
              },
          2:  {2:[0,2,2,1,3,5,4,6],
               1:[3,2,3],
               0:[0,3,2]
              }
          }
	k = 2
	vocab_size = [6,4,7]
	nb_iter = 100
	nb_gibbs_iter = 100
	hmt_gm = HcmMdt(data, k, vocab_size)
	hmt_gm.fit(nb_iter)
	print "-------------------FITTED PARAMS-------------------"
	print("|- PI: "+str(hmt_gm.Pi))
	print("|- P: "+str(hmt_gm.P))

    
    
	print "-------------------BEGIN FIT NEW DATA--------------"
	new_data={0: {2:[0,1,5]
                  },
              1:  {1:[3,2],
                   2:[6,5,4],
                   0:[5]
                  }
              }
	chains_number = 5
	[new_theta, ll] = hmt_gm.fit_newrecords(new_data, nb_iter)
	print ("|-  NEW THETA: "+str(new_theta))
	perpelexity = hmt_gm.perplexity_newrecords(new_data)
	print ("PERPLEXITY UNSEEN DATA "+str(perpelexity))





