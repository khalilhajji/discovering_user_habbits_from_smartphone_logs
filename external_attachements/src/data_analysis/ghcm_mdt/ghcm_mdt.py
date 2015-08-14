#-*- coding: utf-8 -*-

"""
GIBBS SAMPLING IMPLEMENTATION FOR GENERATIVE HIDDEN CLASS MODEL FOR MIXED DATE TYPES (GHCM_MDT)
IMPLEMENTED BY KHALIL HAJJI in 07/2015
"""

import sys
import random as rnd
import gc
from scipy.special import gamma, gammaln, psi
from scipy.stats import *
from scipy import *
import numpy as np
import pdb

class GhcmMdt(object):
    #the convergence threshold rates below which we assume that the system converged
    hyper_parameter_dirichlet_converge_threshold=1e-6
    hyper_parameter_gibbs_converge_threshold=1e-2
    hyper_parameter_llikelihood_converge_threshold = 1e-4

    #the phi and theta returned are averaged between multiple values of phi and theta (i.e after convergence some 
    #loops are made to compute this average).
    #hyper_parameter_number_of_samples_to_average indicates the number of samples of phi and theta taken into account for average.
    hyper_parameter_number_of_samples_to_average = 3
    #hyper_parameter_interval_between_samples_to_average indicates the interval between each to averaging samples
    hyper_parameter_interval_between_samples_to_average = 2
	
    hyper_parameter_number_of_unseen_samples_to_average = 3
    hyper_parameter_interval_between_unseen_samples_to_average = 2
    """
    ----------------------------------INPUT VARIABLES------------------------------------
    data: dictionary data[record_id][feature_id]: Array[values , 1] values of feature that appears in record
          ex [v1,v1,v2,...,v3]
    nb_hclass: number of hidden class required
    vocab_size: Array[nb_features] : the vocabulary size of each feature (1st cell corresponds to voc size of f1
                  2nd cell to voc size of f2,... Fth cell to voc size of fF)

    
    ---------------------------------COMPUTED VARIABLES----------------------------------
    theta: Array [nb_records, nb_hclass] that associates to each record the mix coeffs
           over hidden classes
    phi: dictionary data[feature_id]: Array [nb_hclass, voc_size] that associates to
         each value that can be taken by feature f a probability to appear in hidden
         class k
    alpha: Array [nb_hclass,1]: dirichlet parameters for hidden class distribution in records
    beta: dictionary[feature_id]: Array[voc_size,1]: dirichlet parameters for values distribution
          of feature f in hidden classes
    log_likelihood: double: likelihood of the data after convergence



    ---------------------------------INTERNAL VARIABLES----------------------------------
    hclass_assignements: dictionary data[record_id][feature_id]: Array[values , 1] hidden class assignements of the values of
                         the feature f in record r. ex: [z1,z2,z1,...,zk] which means that 1st value was assigned to 
                         the hidden class 1, the 2nd to the hidden class 2, the 3rd to the hidden class 1 and the last to 
                         the hidden class zk
    cnt_kv: dictionary data[feature_id]: Array [nb_hclass, voc_size] that counts the number of times that a hidden class k was
            assigned to value v
    cnt_rk: Array [nb_records, nb_hclass] that counts the number of times that a hidden class k was
            assigned to record r
    """
    def __init__(self, data, nb_hclass, vocab_size):
        self.nb_hclass = nb_hclass                                  # NUMBER OF HIDDEN CLASSES
        self.vocab_size = vocab_size                                # VOCABULARIES SIZES
        self.data = data                                            #ex: DATA: {DocID: {FeatureID1: [valueID1, valueID1, valueID2 ...],
                                                                    #                   FeatureID2: [valueID1, valueID2, valueID4 ...]}
        self.nb_records = len(self.data)                            # NUMBER OF DOCUMENTS
        self.nb_features = len(vocab_size)                          # NUMBER OF FEATURES
        self.theta = np.zeros((self.nb_records, self.nb_hclass))    # INITIALIZATION FOR THETA MATRIX WITH 0s
        self.alpha = np.empty(self.nb_hclass); self.alpha.fill(0.01);                 # ALPHA INITIALIZATION [0.01, ...., 0.01]                                 
        self.beta = {}
        self.phi = {}
        for f in range(self.nb_features):
            self.beta[f] = np.empty(self.vocab_size[f]); self.beta[f].fill(0.01);    # BETA INITIALIZATION [0.01, ...., 0.01]
            self.phi[f] = np.zeros((self.nb_hclass, self.vocab_size[f]))             # SPACE FOR PHI MATRIX WITH 0s

        self.perplexity = 0.0


    """
    ----------------------------------PUBLIC METHODS------------------------------------
    fit(maxiter, maxiter_gibbs): infer the parameters of GHCM_MDT to fit the data: find optimal values for theta, phi, alpha, beta.
                                       input: maxiter to do for dirichlet params convergence and maxiter_gibbs to do in each iteration
                                       for gibbs convergence
                                       return: the perplexity of the data with the fitted model parameters

    fit_newrecords(self, new_data, maxiter): input: new_data (not seen yet) that has the same format as data 
            (dictionary new_data[record_id][feature_id]) and maxsampels the maximum number of samples allowed to do
            using the model parameters optimized for data, finds the class distribution of the new records
            output: new_theta : Array [nb_newrecords, nb_hclass] that associates to each new record the mix coeffs
            over hidden classes
                    perplexity: the perplexity acheived by the model on the new records
        The fits the class distribution is done using the method proposed in the paper "Improving Gibbs Sampling Predictions on Unseen 
        Data for Latent Dirichlet Allocation" of Yannis Papanikolaou, Timothy N. Rubin and Grigorios Tsoumakas
        We also use the approach described in "Sometimes Average is Best: The Importance of Averaging for Prediction using MCMC Inference
        in Topic Modeling" to have a more accurate Inference
	
	perplexity_newrecords(new_data): computes the perplexity of an unseen data. This metric is an indicator on how well the model
									 generalizes to unseen records. Perplexity is a common criterion for clustering quality and is 
									 often used in the context of hidden class modelling. It is computed as indicated in Blei's paper
									 "Latent Dirichlet Allocation". Note that there is a big conceptual difference between the two
									 concepts introduced by Blei, perplexity and predictive perplexity. In our case, it is the 
									 perplexity which is in interest

    """

    def fit(self, maxiter, maxiter_gibbs):               
        print("# of RECORDS:", self.nb_records)                              # PRINT TRAINING DATA INFORMATION
        print("# of HIDDEN CLASSES:", self.nb_hclass)
        
        #INITIALIZATION: ASSIGN A RANDOM HIDDEN CLASS TO EACH VALUE TAKEN BY EACH FEATURE IN EACH RECORD
        self._assign_random_hclasses()
                
        # COLLAPSED GIBBS SAMPLING
        print("INITIAL STATE")
        print("|- Likelihood:", self._joint_ll())               # FIND (JOINT) LOG-LIKELIHOOD
        for s in range(maxiter): #THIS IS THE BURNIN LOOP (i.e needed for the gibbs sampler to converge)
            self._assign_hclasses(maxiter_gibbs)   #ASSIGN A HIDDEN CLASS TO EACH VALUE OF A FEATURE IN ALL RECORDS (TAKING INTO ACCOUNT ALPHA AND BETA)
            old_alpha = self.alpha
            old_beta = self.beta
            self._estimate_alpha_beta()   # UPDATE ALPHA AND BETA VALUES
            alpha_mean_change = np.mean(abs(self.alpha - old_alpha))
            beta_mean_change = [np.mean(abs(self.beta[f] - old_beta[f])) for f in self.beta.keys()]

            jll = self._joint_ll(); print("SAMPLE #" + str(s)); print("|- Joint Likelihood:", jll)

            if (alpha_mean_change <= GhcmMdt.hyper_parameter_dirichlet_converge_threshold and
                False not in [change <= GhcmMdt.hyper_parameter_dirichlet_converge_threshold for change in beta_mean_change]):
                #the alpha and all the betas mean change is lower than the threshold, so the system has converged->enter into the avergaing mode;
                break
        print("ENTRY IN THE PC MODE, #SAMPLES TO AVERAGE :" + str(GhcmMdt.hyper_parameter_number_of_samples_to_average))
        pc_samples = GhcmMdt.hyper_parameter_number_of_samples_to_average*GhcmMdt.hyper_parameter_interval_between_samples_to_average
        for s in range(pc_samples):  #ENTER IN THE POST CONVERGENCE (PC) MODE
            self._assign_hclasses(maxiter_gibbs) #DO CLASS ASSIGNMENTS FROM THE CONVERGED GIBBS SAMPLER
            jll = self._joint_ll(); print("POST CONVERGENCE SAMPLE #" + str(s)); print("|- Joint Likelihood:", jll)
            if s%GhcmMdt.hyper_parameter_interval_between_samples_to_average==0: #AFTER SOME ASSIGNMENTS, MAKE AN ESTIMATE OF THETA AND PHI
                ph, th = self._estimate_theta_phi() #(i.e enought to assume independence in the assignements that generated the last phi and the actual one)
                self.theta += th
                for f in range(self.nb_features): self.phi[f] += ph[f];


        self.theta /= GhcmMdt.hyper_parameter_number_of_samples_to_average         # AVERAGING GIBBS SAMPLES OF THETA
        for f in range(self.nb_features): self.phi[f]/= GhcmMdt.hyper_parameter_number_of_samples_to_average;  # AVERAGING GIBBS SAMPLES OF PHI

        [marginal_ll, marginal_av_ll] = self._marginal_ll() #COMPUTE THE PERPLEXITY=EXP(-LIKELIHOOD/CORPUS_SIZE)
        self.perplexity = np.exp(-marginal_av_ll)
        
        return self.perplexity


    def fit_newrecords(self, new_data, maxiter, maxiter_gibbs, chains_number):
        nb_new_records = len(new_data)
        final_new_theta = np.zeros((nb_new_records, self.nb_hclass))
        final_perplexity = 0

        for chain in range(chains_number): #RUN A COMPLETE FITTING FROM SCRATCH
            print("CHAIN #" + str(chain));
            new_theta = np.zeros((nb_new_records, self.nb_hclass))
            new_theta_averaged = np.zeros((nb_new_records, self.nb_hclass))

            #INITIALIZATION: ASSIGN A RANDOM HIDDEN CLASS TO EACH VALUE TAKEN BY EACH FEATURE IN EACH RECORD in new data
            [new_hclass_assignements, new_cnt_rk, new_cnt_kv]= self._assign_random_hclasses_for_unseen_records(new_data)
            
            #START FITTING: GOAL ESTIMATING THE THETA OF THE NEW DOCUMENTS
            jll = 1
            for s in range(maxiter):    #THIS IS THE BURNIN LOOP (i.e needed for the gibbs sampler to converge)
                #estimate theta of the new data
                new_theta = self._estimate_theta_for_unseen_records(new_data, new_theta, new_cnt_rk)

                #assign a new hidden class to each value in record taking into account the theta computed
                [new_hclass_assignements, new_cnt_rk, new_cnt_kv]=self._assign_hclass_for_unseen_records(new_data, new_theta, new_cnt_rk, new_cnt_kv, new_hclass_assignements, maxiter_gibbs)
               

                new_jll = self._joint_ll_unseen_data(new_data, new_cnt_rk, new_cnt_kv); jll_change_rate = abs(jll-new_jll)/abs(jll)
                jll = new_jll

                print("SAMPLE #" + str(s)); print("|- Joint Likelihood:", jll); print ("|- CONVERGENCE RATE:", jll_change_rate)

                #test the loglikelihood convergence
                if (jll_change_rate <= GhcmMdt.hyper_parameter_llikelihood_converge_threshold):
                    #system converged --> leave the burnin loop
                    break
            print("ENTRY IN THE PC MODE, #SAMPLES TO AVERAGE :" + str(GhcmMdt.hyper_parameter_number_of_unseen_samples_to_average))                
            pc_samples = GhcmMdt.hyper_parameter_number_of_unseen_samples_to_average*GhcmMdt.hyper_parameter_interval_between_unseen_samples_to_average
            for s in range(pc_samples):      #ENTER IN THE POST CONVERGENCE (PC) MODE
                #DO CLASS ASSIGNMENTS FROM THE CONVERGED GIBBS SAMPLER
                [new_hclass_assignements, new_cnt_rk, new_cnt_kv]=self._assign_hclass_for_unseen_records(new_data, new_theta, new_cnt_rk, new_cnt_kv, new_hclass_assignements, maxiter_gibbs)
                #estimate theta of the new data
                new_theta = self._estimate_theta_for_unseen_records(new_data, new_theta, new_cnt_rk)
                new_jll = self._joint_ll_unseen_data(new_data, new_cnt_rk, new_cnt_kv); print("POST CONVERGENCE SAMPLE #" + str(s)); print("|- Joint Likelihood:", new_jll);

                #we entered into the averaging mode
                if s%GhcmMdt.hyper_parameter_interval_between_unseen_samples_to_average==0:
                    new_theta_averaged += new_theta
                    

            new_theta_averaged /= GhcmMdt.hyper_parameter_number_of_unseen_samples_to_average         # AVERAGING GIBBS SAMPLES OF THETA

            [marginal_ll, marginal_av_ll] = self._marginal_ll_unseen_data(new_data, new_theta_averaged) #COMPUTE MARGINAL LOG LIKELIHOOD
            perplexity = np.exp(-marginal_av_ll)
            print("CHAIN #" + str(chain)); print("|- Perplexity:", perplexity); print("|- Likelihood:", marginal_ll); 
            final_new_theta += new_theta_averaged
        final_new_theta /= chains_number
        [marginal_ll, marginal_av_ll] = self._marginal_ll_unseen_data(new_data, final_new_theta) #COMPUTE MARGINAL LOG LIKELIHOOD
        final_perplexity = np.exp(-marginal_av_ll)
        print("CHAINS DONE"); print("|- Final Perplexity:", final_perplexity); print("|- Likelihood:", marginal_ll);
        
        return [final_new_theta, final_perplexity]
    
    def perplexity_newrecords(self, new_data): #PERPLEXITY NEW RECORDS exp(-(sum(pr(v_new|original_data))/size_new))	
        pr_vnew = dict()
        for f in range(self.nb_features): #PR(V|ORIGINAL_DATA)=Exp[PR(V|R)] (IT IS AN APPROXIMATION)
            pr_vnew[f] = np.sum(np.dot(self.theta,self.phi[f]),0)/self.nb_records
        
        ll=0; size = 0;
        for r in new_data: #LOG_LIKELIHOOD(NEW_DATA) = SUM(LOG(PR(V_new|ORIGINAL DATA)))
            for f in new_data[r]:
                ll+= np.sum(np.log(pr_vnew[f][new_data[r][f]])); size+=len(new_data[r][f])
        perplexity = np.exp(-ll/size)
        return perplexity
    """
    ----------------------------------PRIVATE METHODS USED FOR FITTING THE MODEL------------------------------------
    """   
    def _assign_random_hclasses(self):
        self.hclass_assignements = {}                                  # {INDEX OF DOC: [HIDDEN CLASS ASSIGNMENT]}
        self.cnt_rk = np.zeros((self.nb_records, self.nb_hclass))      # number of assignements of class k to record r
        self.cnt_kv = {}                                               # number of assignments of class k to value v
        for f in range(self.nb_features):
             self.cnt_kv[f] = np.zeros((self.nb_hclass, self.vocab_size[f]))
        
        #ASSIGN A RANDOM HIDDEN CLASS TO EACH VALUE TAKEN BY EACH FEATURE IN EACH RECORD
        for r in self.data:
            self.hclass_assignements[r] = {}
            for f in self.data[r]:
                self.hclass_assignements[r][f]=[]
                for v in self.data[r][f]:
                    k = rnd.randint(0, self.nb_hclass-1)           # RANDOM CLASS ASSIGNMENT        
                    self.hclass_assignements[r][f] += [k]              # RANDOMLY ASSIGN TOPIC TO EACH WORD
                    self.cnt_kv[f][k][v] += 1                        # INCREASE CLASS K COUNT FOR VALUE V OF FEATURE F
                    self.cnt_rk[r][k] += 1                           # INCREASE CLASS K COUNT FOR RECORD R

    def _assign_hclasses(self, maxiter_gibbs):                         # DROW TOPIC SAMPLE FROM FULL-CONDITIONAL DISTRIBUTION
        for s in range(maxiter_gibbs):
            nbchanges = 0.0; corpus_size = 0.0;             #CORPUS SIZE IS THE NUMBER OF ALL THE VALUES PRESENT IN THE CORPUS
            for r in self.data:
                for f in self.data[r]:
                    for pos, v in enumerate(self.data[r][f]):
                        k = self.hclass_assignements[r][f][pos]                           # CLASS ASSIGNMENT OF WORDS FOR EACH DOCUMENT
                        self.cnt_kv[f][k][v] -= 1
                        self.cnt_rk[r][k] -= 1
                        
                        
                        # FULL-CONDITIONAL DISTRIBUTION
                        prc_knowing_r = (self.cnt_rk[r] + self.alpha) / (np.sum(self.cnt_rk[r]) + np.sum(self.alpha)) #estimate of theta
                        prv_knowing_c = (self.cnt_kv[f][:,v] + self.beta[f][v]) / (np.sum(self.cnt_kv[f],1) + np.sum(self.beta[f])) #estimate of phi
                        resp = prc_knowing_r * prv_knowing_c # RESP represents the responsability of value v of feature f in record r at position pos in generating c
                        resp /= np.sum(resp)                 # to obtain probability Pr(Z=c|(v,pos,f,r))
                        # NOTE: 'resp' is MULTINOMIAL DISTRIBUTION WITH THE LENGTH, NUMBER OF nb_hclass
                        new_k = np.random.multinomial(1, resp).argmax()       # RANDOM SAMPLING FROM FULL-CONDITIONAL DISTRIBUTION
                        self.hclass_assignements[r][f][pos] = new_k
                        self.cnt_kv[f][new_k][v] += 1
                        self.cnt_rk[r][new_k] += 1
                        corpus_size += 1
                        if new_k!=k : nbchanges+=1;
            if((nbchanges/corpus_size) <= GhcmMdt.hyper_parameter_gibbs_converge_threshold): break; #LEAVE LOOP IF CONVERGENCE

    def _joint_ll(self):           #FIND (JOINT) LOG-LIKELIHOOD VALUE  LOG(PR(DATA, ASSIGNMENTS|ALPHA, BETA) )
        ll = 0

        for f in range(self.nb_features): #Pr(corpus|assignments)
            for k in range(self.nb_hclass):                                #LOG(PR(DATA| ASSIGNEMENTS, ALPHA, BETA))
                ll += gammaln(np.sum(self.beta[f]))
                ll -= np.sum(gammaln(self.beta[f]))
                ll += np.sum(gammaln(self.cnt_kv[f][k] + self.beta[f]))
                ll -= gammaln(np.sum(self.cnt_kv[f][k] + self.beta[f]))
        for r in self.data:  #Pr(assignments)                                #LOG(PR(ASSIGNEMENTS|ALPHA, BETA))
            ll += gammaln(np.sum(self.alpha))
            ll -= np.sum(gammaln(self.alpha))
            ll += np.sum(gammaln(self.cnt_rk[r] + self.alpha))
            ll -= gammaln(np.sum(self.cnt_rk[r] + self.alpha))
        return ll   #LOG(PR(DATA, ASSIGNMENTS|ALPHA, BETA))=LOG(PR(DATA| ASSIGNEMENTS, ALPHA, BETA)) + LOG(PR(ASSIGNEMENTS|ALPHA, BETA))

    def _marginal_ll(self): #COMPUTE MARGINAL LOG LIKELIHOOD IS PR(DATA|ALPHA, BETA)
        ll = 0                              #WE COMPUTED BY SUMMING LOG(PR(V)= SUMk(PR(V|Zk)*PR(ZK|r))) CONSIDERING THE DISTRIBUTIONS PHI AND THETA
        size = 0
        for r in self.data:
            for f in self.data[r]:
                for v in self.data[r][f]:
                    ll+=  np.log(np.dot(self.theta[r], self.phi[f][:,v]))                          #LOG(PR(V)= SUMk(PR(V|Zk)*PR(ZK|r)))
                    size +=1
        av_ll = ll/size                     #av_ll represents the likelihood by value
        return [ll , av_ll]

    def _estimate_alpha_beta(self):
        # ADJUST ALPHA AND BETA BY USING MINKA'S FIXED-POINT ITERATION
        numerator = 0; denominator = 0; previous_min = np.min(self.alpha)
        for r in range(self.nb_records):
            numerator += psi(self.cnt_rk[r] + self.alpha) - psi(self.alpha)
            denominator += psi(np.sum(self.cnt_rk[r] + self.alpha)) - psi(np.sum(self.alpha))
        self.alpha = self.alpha * (numerator / denominator)                       # UPDATE ALPHA

        if 0 in self.alpha:         #THIS CASE IS VERY RARE AND HAPPENS WHERE A HIDDEN CLASS K HAS RECEIVED 0 ASSIGNMENTS
            print ("|----WARNING: alpha = 0 encountered") #FORCE THE 0 ALPHAS TO THE MINIMUM BETWEEN (THE SMALLEST NON NULL APLHA, 1/NB_RECORDS,
            self.alpha[self.alpha==0] = min(previous_min,np.min(self.alpha[self.alpha>0]), 1.0/self.nb_records) #AND THE SMALLEST APLHA BEFORE UPDATE

        for f in range(self.nb_features):
            numerator = 0; denominator = 0; previous_min = np.min(self.beta[f])
            for k in range(self.nb_hclass):
                numerator += psi(self.cnt_kv[f][k] + self.beta[f]) - psi(self.beta[f])
                denominator += psi(np.sum(self.cnt_kv[f][k] + self.beta[f])) - psi(np.sum(self.beta[f]))
            self.beta[f] = self.beta[f] * (numerator /denominator)       # UPDATE BETA
			
            if 0 in self.beta[f]:         #THIS CASE IS VERY RARE AND HAPPENS WHERE A VALUE DO NOT HAVE ANY OCCURENCE IN THE CORPUS
                print ("|----WARNING: beta = 0 encountered") #FORCE THE 0 BETAS TO THE MINIMUM BETWEEN (THE SMALLEST NON NULL APLHA, 1/NB_VALUES,
                self.beta[f][self.beta[f]==0] = min(previous_min,np.min(self.beta[f][self.beta[f]>0]), 1.0/self.vocab_size[f]) #AND THE SMALLEST APLHA BEFORE UPDATE

    def _estimate_theta_phi(self):
        th = np.zeros((self.nb_records, self.nb_hclass))                     # SPACE FOR THETA
        ph = {}                                                              # SPACE FOR PHI
        for r in range(self.nb_records):
            for k in range(self.nb_hclass):
                th[r][k] = (self.cnt_rk[r][k] + self.alpha[k]) / (np.sum(self.cnt_rk[r]) + np.sum(self.alpha))
        
        for f in range(self.nb_features):
            ph[f]= np.zeros((self.nb_hclass, self.vocab_size[f]))             # SPACE FOR PHI
            for k in range(self.nb_hclass):
                for v in range(self.vocab_size[f]):
                    ph[f][k][v] = (self.cnt_kv[f][k][v] + self.beta[f][v]) / (np.sum(self.cnt_kv[f][k]) + np.sum(self.beta[f]))
        return ph, th

    """
    ----------------------------------PRIVATE METHODS USED FOR TRATING UNSEEN DATA------------------------------------
    """ 
    def _assign_random_hclasses_for_unseen_records(self, new_data):
        # ASSIGN A RANDOM HIDDEN CLASS TO EACH VALUE OF EACH RECORD
        #Here note that we do not keep count of the number of classes assigned to each value.
        nb_new_records = len(new_data)
        new_hclass_assignements = {}                                            # {INDEX OF DOC: [HIDDEN CLASS ASSIGNMENT]}
        new_cnt_rk = np.zeros((nb_new_records, self.nb_hclass))             # number of assignements of class k to record r
        new_cnt_kv= {}                                                      # number of assignments of class k to value v
        for f in range(self.nb_features):
             new_cnt_kv[f] = np.zeros((self.nb_hclass, self.vocab_size[f]))

        for r in new_data:
            new_hclass_assignements[r] = {}
            for f in new_data[r]:
                new_hclass_assignements[r][f]=[]
                for v in new_data[r][f]:
                    k = rnd.randint(0, self.nb_hclass-1)          # RANDOM HIDDEN CLASS ASSIGNMENT
                    new_hclass_assignements[r][f] += [k]             # RANDOMLY ASSIGN TOPIC TO EACH WORD
                    new_cnt_rk[r][k]+=1                              # INCREASE CLASS K COUNT FOR RECORD R
                    new_cnt_kv[f][k][v]+=1                           # INCREASE CLASS K COUNT FOR VALUE V
        return [new_hclass_assignements, new_cnt_rk, new_cnt_kv]

    def _assign_hclass_for_unseen_records(self, new_data, theta, cnt_rk, cnt_vk, hclass_assignements, maxiter_gibbs):
        for iter in range(maxiter_gibbs):
            #assign a new hidden class to each value in record taking into account the theta computed
            for r in new_data:
                for f in new_data[r]:
                    for pos, v in enumerate(new_data[r][f]):
                        k = hclass_assignements[r][f][pos]                           # CLASS ASSIGNMENT OF WORDS FOR EACH DOCUMENT
                        cnt_rk[r][k] -= 1
                        cnt_vk[f][k][v] -=1
                        
                        # FULL-CONDITIONAL DISTRIBUTION
                        resp = theta[r] * self.phi[f][: , v] # RESP represents the responsability of value v of feature f in record r at position pos in generating c: Pr()
                        resp /= np.sum(resp)                 # to obtain probability Pr(Z=c|(v,pos,f,r))
                            
                        # NOTE: 'resp' is MULTINOMIAL DISTRIBUTION WITH THE LENGTH, NUMBER OF nb_hclass
                        new_k = np.random.multinomial(1, resp).argmax()       # RANDOM SAMPLING FROM FULL-CONDITIONAL DISTRIBUTION
                        hclass_assignements[r][f][pos] = new_k
                        cnt_rk[r][new_k] += 1                
                        cnt_vk[f][new_k][v] +=1

        return [hclass_assignements, cnt_rk, cnt_vk]

    def _joint_ll_unseen_data(self, new_data, cnt_rk, cnt_vk): #FIND (JOINT) LOG-LIKELIHOOD VALUE  LOG(PR(DATA, ASSIGNMENTS|ALPHA, BETA))
        ll = 0 
        for f in range(self.nb_features):                       #LOG(PR(DATA| ASSIGNEMENTS, ALPHA, BETA))
            for k in range(self.nb_hclass):                                
                ll += gammaln(np.sum(self.beta[f]))
                ll -= np.sum(gammaln(self.beta[f]))
                ll += np.sum(gammaln(cnt_vk[f][k] + self.beta[f]))
                ll -= gammaln(np.sum(cnt_vk[f][k] + self.beta[f]))
        for r in new_data:                                     #LOG(PR(ASSIGNEMENTS|ALPHA, BETA))
            ll += gammaln(np.sum(self.alpha))
            ll -= np.sum(gammaln(self.alpha))
            ll += np.sum(gammaln(cnt_rk[r] + self.alpha))
            ll -= gammaln(np.sum(cnt_rk[r] + self.alpha))
        return ll          #LOG(PR(DATA, ASSIGNMENTS|ALPHA, BETA))=LOG(PR(DATA| ASSIGNEMENTS, ALPHA, BETA)) + LOG(PR(ASSIGNEMENTS|ALPHA, BETA))

   
    def _marginal_ll_unseen_data(self, new_data, theta):  #COMPUTE MARGINAL LOG LIKELIHOOD IS PR(DATA|ALPHA, BETA)
        ll = 0                              #WE COMPUTED BY SUMMING LOG(PR(V)= SUMk(PR(V|Zk)*PR(ZK|r))) CONSIDERING THE DISTRIBUTIONS PHI AND THETA
        size = 0
        for r in new_data:
            for f in new_data[r]:
                for v in new_data[r][f]:
                    ll+=  np.log(np.dot(theta[r], self.phi[f][:,v]))                          #LOG(PR(V)= SUMk(PR(V|Zk)*PR(ZK|r)))
                    size +=1
        av_ll = ll/size                     #av_ll represents the likelihood by value
        return [ll , av_ll]

    def _estimate_theta_for_unseen_records(self, new_data, theta, cnt_rk):  
        for r in new_data:
            #I- estimate theta of record r
            #estimate responsabilities of each value to generate each hidden class Pr(Zk|v,f,r)
            prc_knowing_r = (cnt_rk[r]+self.alpha)/(np.sum(cnt_rk[r])+np.sum(self.alpha))
            for f in new_data[r]:
                for pos, v in enumerate(new_data[r][f]):
                    resp = self.phi[f][: , v] * prc_knowing_r #Pr(Zk|v,f,r) proportional to Pr(v|Zk).Pr(Zk|r)
                    resp /= np.sum(resp)                      #normalize to obtain a proba
                    theta[r] += resp                      #theta prop to sum(resp) over different values

            #noramlize theta to obtain probabilities
            theta[r] /= np.sum(theta[r])
        return theta



    
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
    ghmt_gm = GhcmMdt(data, k, vocab_size)
    ghmt_gm.fit(nb_iter, nb_gibbs_iter)
    print "-------------------FITTED PARAMS-------------------"
    print("|- THETA: "+str(ghmt_gm.theta))
    print("|- PHI: "+str(ghmt_gm.phi))

    
    print "-------------------BEGIN FIT NEW DATA--------------"
    new_data={0: {2:[0,1,5]
                  },
              1:  {1:[3,2],
                   2:[6,5,4],
                   0:[5]
                  }
              }
    chains_number = 5
    [new_theta, ll] = ghmt_gm.fit_newrecords(new_data, nb_iter, nb_gibbs_iter, chains_number)
    print ("|-  NEW THETA: "+str(new_theta))
    perpelexity = ghmt_gm.perplexity_newrecords(new_data)
    print ("PERPLEXITY UNSEEN DATA "+str(perpelexity))


