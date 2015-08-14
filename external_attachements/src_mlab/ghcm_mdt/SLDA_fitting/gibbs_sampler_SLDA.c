#include "mex.h"
#include "gibbs_sampler_LDA_rand.c"
#include "math.h"
#include "float.h"

/*
 * Syntax (for details see gibbs_sampler_SLDA.m file)
 * [WP, DP, ZOUT] = gibbs_sampler_SLDA(WS, DS, N_TOPICS, N_ITER, ALPHA, BETA, SEED, OUTPUT, ZIN,
 *      RATED_DOCS, YS, ETA, SIGMA2)
 */


/* ###################################################################### */
/* ###                      Computational routine                     ### */
/* ###################################################################### */

/*
 * Most interesting variables (indexing starting from 0, not as matlab!):
 *  ds: array of length N_TOKENS, containing document indices (between 0 and D-1)!
 *  ws: array of length N_TOKENS, containing word indices (between 0 and W-1)!
 *
 *  z: array of length N_TOKENS, containing topic indices (between 0 and N_TOPICS-1)!
 *
 *  dp: array of length N_TOPICS*D, containing number of tokens assigned to
 *      topic k and document d (at index d*N_TOPICS + k, d and k starting at 0)
 *  wp: array of length N_TOPICS*W, containing number of tokens assigned to
 *      topic k and word w (at index w*N_TOPICS + k, w and k starting at 0)
 *
 * Note that (only) z, wp and dp are (transformed and) returned by the global function
 * Note that randomMT has be initialized with a seed outside
 */
void gibbs_sampler_SLDA(double ALPHA, double BETA, int W, int N_TOPICS, int D,
        int N_ITER, int OUTPUT, int N_TOKENS, int *ds, int *ws,
        int *z, int *wp, int *dp,  /* Variables for input and output */
        double *RATED_DOCS, double* YS, double *ETA, double SIGMA2) {
    
    /* Local variables */
    int i,j,k,iToken;
    int topic, newTopic, randi, temp, iter, wiOffset, diOffset;
    double totProb, WBETA, rand, cumSum;
    int *ztot; /* Number of tokens assigned to each topic */
    int *order; /* Order according to which we sample tokens (permutation of 1..N_TOKENS) */
    double *probs; /* Unnormalized probabilities of each topic for a given token, which we use to sample */
    
    /* Local variables for sLDA */
    int *n_tokens_by_doc; /* important: precomputing number of tokens by document */
    int doc;
    int N_d;
    double y; /* the rating */
    double *lp_y_given_z;
    double *p_y_given_z;
    double y_d;
    double tmp_double;
    double max_lp_y;
    
    /* Initialize arrays */
    ztot  = (int *) mxCalloc(N_TOPICS, sizeof(int)); /* N_TOPICS int */
    order  = (int *) mxCalloc(N_TOKENS, sizeof(int)); /* N_TOKENS int */
    probs  = (double *) mxCalloc(N_TOPICS, sizeof(double)); /* N_TOPICS double */
    n_tokens_by_doc = (int *) mxCalloc(D, sizeof(int)); /* D int */
    lp_y_given_z  = (double *) mxCalloc(N_TOPICS, sizeof(double)); /* N_TOPICS double */
    p_y_given_z  = (double *) mxCalloc(N_TOPICS, sizeof(double)); /* N_TOPICS double */
    
    /* Build the count matrices (and ztot) from previous topic assignation z */
    for (i=0; i<N_TOKENS; i++) {
        topic = z[i];
        wp[ws[i]*N_TOPICS + topic]++; /* increment wp count matrix */
        dp[ds[i]*N_TOPICS + topic]++; /* increment dp count matrix */
        ztot[topic]++; /* increment ztot matrix */
    }
    
    /* Precompute the number of tokens per document */
    for (i=0; i<D; i++) {
        n_tokens_by_doc[i] = 0;
        for (j=0; j<N_TOPICS; j++) {
            n_tokens_by_doc[i] += dp[i*N_TOPICS + j];
        }
    }
    
    /* Precompute constant W*BETA */
    WBETA = (double) (W*BETA);
    
    /* Generate a random permutation of 1:N_TOKENS */
    /* (=> random update sequence, same for all iterations!) */
    for (i=0; i<N_TOKENS; i++) {
        order[i]=i; /* fill with increasing series */
    }
    for (i=0; i<(N_TOKENS-1); i++) {
        /* pick a random integer between i and N_TOKENS */
        randi = i + (int) ((double) (N_TOKENS-i) * (double) randomMT() / (double) (4294967296.0 + 1.0));
        
        /* switch contents on position i and position randi */
        temp = order[randi];
        order[randi]=order[i];
        order[i]=temp;
    }
    
    /* Performs N_ITER iterations over all the tokens */
    for (iter=0; iter<N_ITER; iter++) {
        if (OUTPUT >=1) {
            if ((iter % 10)==0) {
                mexPrintf("\tIteration %d of %d\n", iter, N_ITER);
                mexEvalString("drawnow;");
            }
        }
        
        /* Iterate over all tokens, according to 'order' */
        for (i = 0; i < N_TOKENS; i++) {
            /* Get the index of the current token to assess */
            iToken = order[i];
            
            /* Get the current topic assigned to token */
            topic = z[iToken];
            
            /* Get the current doc assigned to token */
            doc = ds[iToken];
            
            /* Precompute offsets */
            wiOffset = ws[iToken]*N_TOPICS; /* offset for current word in wp matrix */
            diOffset = doc*N_TOPICS; /* offset for current doc in dp matrix */
            
            /* Update counts (remove current token) */
            ztot[topic]--;  /* substract from counts sums */
            wp[wiOffset + topic]--;
            dp[diOffset + topic]--;
            
            /* Check whether the document of this token has an associated rating */
            if(RATED_DOCS[doc] == 1) {
                y = YS[doc];
                N_d = n_tokens_by_doc[doc];
                
                /* First compute exponent (work in log-domain) */
                for(j = 0; j < N_TOPICS; j++) {
                    dp[diOffset + j]++;
                    
                    tmp_double = 0;
                    for (k = 0; k < N_TOPICS; k++){
                        tmp_double += ETA[k] * dp[diOffset + k];
                    }
                    
                    tmp_double /= N_d;
                    tmp_double -= y;
                    lp_y_given_z[j] = -tmp_double*tmp_double/2/SIGMA2;
                    
                    /* mexPrintf("\t p_y_given_z: %f\n", p_y_given_z); */
                    
                    dp[diOffset + j]--;
                }
                
                /* Rescale log proba, to avoid that everything becomes 0 when using exp() */
                max_lp_y = -DBL_MAX; /* Find the maximum */
                for(j = 0; j < N_TOPICS; j++) {
                    if(lp_y_given_z[j] > max_lp_y) {
                        max_lp_y = lp_y_given_z[j];
                    }
                }
                for(j = 0; j < N_TOPICS; j++) {
                    lp_y_given_z[j] -= max_lp_y;
                }
                
                /* Finally exponentiate */
                for(j = 0; j < N_TOPICS; j++) {
                    p_y_given_z[j] = exp(lp_y_given_z[j]);
                }
            } else {
                for(j = 0; j < N_TOPICS; j++) {
                    p_y_given_z[j] = 1;
                }
            }
            
            /* !!! Compute the (unormalized) conditional probas (see paper) !!! */
            totProb = (double) 0;
            for (j = 0; j < N_TOPICS; j++) {
                probs[j] = ((double) wp[wiOffset + j] + (double) BETA)
                / ((double) ztot[j] + (double) WBETA)
                * ((double) dp[diOffset + j] + (double) ALPHA)
                * p_y_given_z[j];
                
                totProb += probs[j];
            }
            
            /* Sample a topic from the resulting (unormalized) distribution */
            /* Generate a random number 'rand' in [0, totProb] and find the topic */
            /* for which the cumulative proba sum(probs(topic_i)) exceed 'rand' */
            rand = (double) totProb * (double) randomMT() / (double) 4294967296.0;
            cumSum = probs[0];
            newTopic = 0;
            while (rand > cumSum) {
                newTopic++;
                cumSum += probs[newTopic];
            }
            
            /* Assign new topic current token */
            z[iToken] = newTopic;
            
            /* Update counts (add newly sampled token) */
            ztot[newTopic]++;
            wp[wiOffset + newTopic]++;
            dp[diOffset + newTopic]++;
        }
    }
}


/* ###################################################################### */
/* ###                          Gateway routine                       ### */
/* ###################################################################### */

/*
 * Syntax (for details see gibbs_sampler_SLDA.m file)
 * [WP, DP, ZOUT] = gibbs_sampler_SLDA(WS, DS, N_TOPICS, N_ITER, ALPHA, BETA, SEED, OUTPUT, ZIN)
 */
void mexFunction(int nlhs, mxArray *plhs[], int nrhs,
        const mxArray *prhs[]) {
    
    double *ZOUT, *WS, *DS, *ZIN, *tmpPr;
    double ALPHA,BETA;
    mwIndex *tmpIr, *tmpJc;
    int *z,*ds,*ws, *wp, *dp;
    int W, N_TOPICS, D, N_ITER, SEED, OUTPUT, nzmax, nzmaxwp, nzmaxdp, N_TOKENS;
    int i, j, c, n, nt; /* Counter variables */
    
    double *RATED_DOCS; /* TODO semantically, this is an int array */
    double *YS;
    double *ETA;
    double SIGMA2;
    
    /* CHECK AND IMPORT INPUT */
    /* Check for proper number of arguments. */
    if (nrhs != 13) {
        mexErrMsgTxt("13 input arguments required");
    } else if (nlhs != 3) {
        mexErrMsgTxt("3 output arguments required");
    }
    
    /* process the input arguments */
    if (mxIsDouble(prhs[0]) != 1) {
        mexErrMsgTxt("WS input vector must be a double precision matrix");
    }
    if (mxIsDouble(prhs[1]) != 1) {
        mexErrMsgTxt("DS input vector must be a double precision matrix");
    }
    
    /* pointer to word indices */
    WS = mxGetPr(prhs[0]);
    
    /* pointer to document indices */
    DS = mxGetPr(prhs[1]);
    
    /* get the number of tokens */
    N_TOKENS = mxGetM(prhs[0]) * mxGetN(prhs[0]);
    if (N_TOKENS == 0) {
        mexErrMsgTxt("WS vector is empty");
    }
    if (N_TOKENS != (mxGetM(prhs[1]) * mxGetN(prhs[1]))) {
        mexErrMsgTxt("WS and DS vectors should have same number of entries");
    }
    
    N_TOPICS    = (int) mxGetScalar(prhs[2]);
    if (N_TOPICS<=0) {
        mexErrMsgTxt("Number of topics must be greater than zero");
    }
    
    N_ITER    = (int) mxGetScalar(prhs[3]);
    if (N_ITER<0) {
        mexErrMsgTxt("Number of iterations must be positive");
    }
    
    ALPHA = (double) mxGetScalar(prhs[4]);
    if (ALPHA<=0) {
        mexErrMsgTxt("ALPHA must be greater than zero");
    }
    
    BETA = (double) mxGetScalar(prhs[5]);
    if (BETA<=0) {
        mexErrMsgTxt("BETA must be greater than zero");
    }
    
    SEED = (int) mxGetScalar(prhs[6]);
    
    OUTPUT = (int) mxGetScalar(prhs[7]);
    
    ZIN = mxGetPr(prhs[8]);
    if (N_TOKENS != (mxGetM(prhs[8]) * mxGetN(prhs[8]))) {
        mexErrMsgTxt("WS and ZIN vectors should have same number of entries");
    }
    
    RATED_DOCS = mxGetPr(prhs[9]); /* int array of size D */
    YS = mxGetPr(prhs[10]); /* double array of size D */
    ETA = mxGetPr(prhs[11]); /* double array of size N_TOPICS */
    SIGMA2 = (double) mxGetScalar(prhs[12]);
    
    /* PREPARE/CONVERT INTERNAL VARIABLES */
    /* count the vocabulary size W (find max) */
    W = 0;
    for (i=0; i<N_TOKENS; i++) {
        if (WS[i] > W) {
            W = WS[i];
        }
    }
    
    /* count the number of documents D (find max) */
    D = 0;
    for (i=0; i<N_TOKENS; i++) {
        if (DS[i] > D) {
            D = DS[i];
        }
    }
    
    /* allocate memory */
    z  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    ds  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    ws  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    
    wp  = (int *) mxCalloc(N_TOPICS*W, sizeof(int)); /* word count matrix (non-sparse) */
    dp  = (int *) mxCalloc(N_TOPICS*D, sizeof(int)); /* doc count matrix (non-sparse) */
    
    if (OUTPUT==2) {
        mexPrintf("Internal Memory Allocation\n");
        mexPrintf("\tw,d,z,order indices combined = %d bytes\n", 4 * sizeof(int) * N_TOKENS);
        mexPrintf("\twp (full) matrix = %d bytes\n", sizeof(int) * W * N_TOPICS );
        mexPrintf("\tdp (full) matrix = %d bytes\n", sizeof(int) * D * N_TOPICS );
    }
    
    /* copy over the word/doc/topic indices into internal format (indices starting from 0!)*/
    for (i=0; i<N_TOKENS; i++) {
        z[i] = (int) ZIN[i] - 1;
        ws[i] = (int) WS[i] - 1;
        ds[i] = (int) DS[i] - 1;
    }
    
    /* RUN THE SAMPLER */
    /* seeding */
    seedMT(1 + SEED * 2); /* seeding only works on odd numbers */
    
    gibbs_sampler_SLDA(ALPHA, BETA, W, N_TOPICS, D, N_ITER, OUTPUT, N_TOKENS, ds, ws, /* Variables only for input */
            z, wp, dp, /* Variables for input and output */
            RATED_DOCS, YS, ETA, SIGMA2);
    
    
    /* CONVERT THE OUTPUT */
    /* convert the full wp matrix into a sparse matrix */
    nzmaxwp = 0; /* Count the number of nonzero entries */
    for (i=0; i<W*N_TOPICS; i++) {
        if(wp[i] > 0){
            nzmaxwp++;
        }
    }
    
    plhs[0] = mxCreateSparse(W, N_TOPICS, nzmaxwp, mxREAL);
    tmpPr  = mxGetPr(plhs[0]);
    tmpIr = mxGetIr(plhs[0]);
    tmpJc = mxGetJc(plhs[0]);
    n = 0;
    for (j=0; j<N_TOPICS; j++) {
        tmpJc[j] = n;
        for (i=0; i<W; i++) {
            c = (int) wp[i*N_TOPICS + j];
            if (c > 0) {
                tmpPr[n] = c;
                tmpIr[n] = i;
                n++;
            }
        }
    }
    tmpJc[N_TOPICS] = n;
    
    /* convert the full dp matrix into a sparse matrix */
    nzmaxdp = 0;
    for (i=0; i<D*N_TOPICS; i++) {
        if(dp[i] > 0){
            nzmaxdp++;
        }
    }
    
    plhs[1] = mxCreateSparse(D, N_TOPICS, nzmaxdp, mxREAL);
    tmpPr  = mxGetPr(plhs[1]);
    tmpIr = mxGetIr(plhs[1]);
    tmpJc = mxGetJc(plhs[1]);
    n = 0;
    for (j=0; j<N_TOPICS; j++) {
        tmpJc[j] = n;
        for (i=0; i<D; i++) {
            c = (int) dp[i*N_TOPICS + j];
            if (c > 0) {
                tmpPr[n] = c;
                tmpIr[n] = i;
                n++;
            }
        }
    }
    tmpJc[N_TOPICS] = n;
    
    /* create double matrix, and convert z from int to double (and shift to have value in 1..N_TOPICS) */
    plhs[2] = mxCreateDoubleMatrix(N_TOKENS, 1, mxREAL);
    ZOUT = mxGetPr(plhs[2]);
    for (i=0; i<N_TOKENS; i++){
        ZOUT[i] = (double) z[i] + 1;
    }
}
