#include "mex.h"
#include "gibbs_sampler_LDA_rand.c"


/* ###################################################################### */
/* ###                      Computational routine                     ### */
/* ###################################################################### */

/*
 * Most interesting variables (indexing starting from 0, not as matlab!):
 *  docs_vector: array of length N_TOKENS, containing document indices (between 0 and N_DOCS-1)!
 *  words_vector: array of length N_TOKENS, containing word indices (between 0 and VOC_SIZE-1)!
 *
 *  topics_vector: array of length N_TOKENS, containing topic indices (between 0 and N_TOPICS-1)!
 *
 *  docs_counts: array of length N_TOPICS*N_DOCS, containing number of tokens assigned to 
 *      topic k and document d (at index d*N_TOPICS + k, d and k starting at 0)
 *  words_counts: array of length N_TOPICS*VOC_SIZE, containing number of tokens assigned to 
 *      topic k and word w (at index w*N_TOPICS + k, w and k starting at 0)
 *
 *  phi: array of length VOC_SIZE*N_TOPICS, containing the probability of having
 *       word w in topic k (at index k*N_WORDS + w, w and k starting at 0)
 *
 * Note that (only) topics_vector, words_counts and docs_counts are (transformed and) returned by the global function
 * Note that randomMT has be initialized with a seed outside
 */
void gibbs_sampler_fixed_LDA(double ALPHA, int VOC_SIZE, int N_TOPICS, int N_DOCS,
        int N_SWEEPS, int DISPLAY_OUTPUT, int N_TOKENS, int *docs_vector, int *words_vector, double *phi,
        int *topics_vector, int *docs_counts) {  /* Variables for input and output */
    
    /* Local variables */
    int i,j,iToken;
    int topic, newTopic, randi, temp, iter, wi, diOffset;
    double totProb, rand, cumSum;    
    int *ztot; /* Number of tokens assigned to each topic */
    int *order; /* Order according to which we sample tokens (permutation of 1..N_TOKENS) */
    double *probs; /* Unnormalized probabilities of each topic for a given token, which we use to sample */
    
    /* Initialize arrays */
    ztot  = (int *) mxCalloc(N_TOPICS, sizeof(int)); /* N_TOPICS int */
    order  = (int *) mxCalloc(N_TOKENS, sizeof(int)); /* N_TOKENS int */
    probs  = (double *) mxCalloc(N_TOPICS, sizeof(double)); /* N_TOPICS double */
    
    /* Build the count matrices (and ztot) from previous topic assignation z */
    for (i=0; i<N_TOKENS; i++) {
        topic = topics_vector[i];
        docs_counts[docs_vector[i]*N_TOPICS + topic]++; /* increment docs_counts matrix */
        ztot[topic]++; /* increment ztot matrix */
    }
    
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
    
    /* Performs N_SWEEPS over all the tokens */
    for (iter=0; iter<N_SWEEPS; iter++) {
        if (DISPLAY_OUTPUT >=1) {
            if ((iter % 10)==0) {
                mexPrintf("\tSweep %d of %d\n", iter, N_SWEEPS);
                mexEvalString("drawnow;");
            }
        }
        
        /* Iterate over all tokens, according to 'order' */
        for (i = 0; i < N_TOKENS; i++) {
            /* Get the index of the current token to assess */
            iToken = order[i]; 
            
            /* Get the current topic assigned to token */
            topic = topics_vector[iToken]; 
            
            /* Precompute offsets */
            wi = words_vector[iToken]; /* current word */
            diOffset = docs_vector[iToken]*N_TOPICS; /* offset for current doc in docs_counts matrix */
            
            /* Update counts (remove current token) */
            ztot[topic]--;  /* substract from counts sums */
            docs_counts[diOffset + topic]--;
            
            /* !!! Compute the (unormalized) conditional probas (see paper) !!! */
            totProb = (double) 0;
            for (j = 0; j < N_TOPICS; j++) {
                probs[j] = phi[j*VOC_SIZE + wi] * 
                        ((double) docs_counts[diOffset + j] + (double) ALPHA);
                
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
            topics_vector[iToken] = newTopic;
            
            /* Update counts (add newly sampled token) */
            ztot[newTopic]++;
            docs_counts[diOffset + newTopic]++;
        }
    }
}


/* ###################################################################### */
/* ###                          Gateway routine                       ### */
/* ###################################################################### */

/*
% [docs_counts, topics_vector_out] = gibbs_sampler_fixed_LDA(...
%   words_vector, docs_vector, N_TOPICS, N_SWEEPS, ALPHA, ...
%   SEED, DISPLAY_OUTPUT, topics_vector_in)
% 
% INPUT
%   words_vector        N_TOKENS x 1 vector
%   docs_vector         N_TOKENS x 1 vector
%   N_TOPICS            scalar
%   N_SWEEPS            scalar
%   ALPHA               scalar
%   SEED                scalar
%   DISPLAY_OUTPUT      scalar
%   topics_vector_in    N_TOKENS x 1 vector
% 
% OUTPUT
%   docs_counts         N_DOCS   x N_TOPICS matrix
%   topics_vector_out   N_TOKENS x 1 vector
 */
void mexFunction(int nlhs, mxArray *plhs[], int nrhs,
        const mxArray *prhs[]) {
    
    double *topics_vector_out, *words_vector1, *docs_vector1, *topics_vector_in, *tmpPr, *phi;
    double ALPHA;
    mwIndex *tmpIr, *tmpJc;
    int *topics_vector,*docs_vector,*words_vector, *docs_counts;
    int VOC_SIZE, N_TOPICS, N_DOCS, N_SWEEPS, SEED, DISPLAY_OUTPUT, nzmax, nzmaxwp, nzmaxdp, N_TOKENS;
    int i, j, c, n, nt; /* Counter variables */
    
    /* CHECK AND IMPORT INPUT */
    /* Check for proper number of arguments. */
    if (nrhs != 9) {
        mexErrMsgTxt("9 input arguments required");
    } else if (nlhs != 2) {
        mexErrMsgTxt("2 output arguments required");
    }
    
    /* process the input arguments */
    if (mxIsDouble(prhs[0]) != 1) {
        mexErrMsgTxt("words_vector input vector must be a double precision matrix");
    }
    if (mxIsDouble(prhs[1]) != 1) {
        mexErrMsgTxt("docs_vector input vector must be a double precision matrix");
    }
    
    /* pointer to word indices */
    words_vector1 = mxGetPr(prhs[0]);
    
    /* pointer to document indices */
    docs_vector1 = mxGetPr(prhs[1]);
    
    /* get the number of tokens */
    N_TOKENS = mxGetM(prhs[0]) * mxGetN(prhs[0]);
    if (N_TOKENS == 0) {
        mexErrMsgTxt("words_vector vector is empty");
    }
    if (N_TOKENS != (mxGetM(prhs[1]) * mxGetN(prhs[1]))) {
        mexErrMsgTxt("words_vector and docs_vector vectors should have same number of entries");
    }
    
    N_TOPICS    = (int) mxGetScalar(prhs[2]);
    if (N_TOPICS<=0) {
        mexErrMsgTxt("Number of topics must be greater than zero");
    }
    
    N_SWEEPS    = (int) mxGetScalar(prhs[3]);
    if (N_SWEEPS<0) {
        mexErrMsgTxt("Number of iterations must be positive");
    }
    
    ALPHA = (double) mxGetScalar(prhs[4]);
    if (ALPHA<=0) {
        mexErrMsgTxt("ALPHA must be greater than zero");
    }
        
    SEED = (int) mxGetScalar(prhs[5]);
    
    DISPLAY_OUTPUT = (int) mxGetScalar(prhs[6]);
    
    topics_vector_in = mxGetPr(prhs[7]);
    if (N_TOKENS != (mxGetM(prhs[7]) * mxGetN(prhs[7]))) {
        mexErrMsgTxt("words_vector and topics_vector_in vectors should have same number of entries");
    }
    
    phi = mxGetPr(prhs[8]); /* VOC_SIZExN_TOPICS matrix */
    
    /* PREPARE/CONVERT INTERNAL VARIABLES */
    /* count the vocabulary size VOC_SIZE (find max) */
    VOC_SIZE = 0;
    for (i=0; i<N_TOKENS; i++) {
        if (words_vector1[i] > VOC_SIZE) {
            VOC_SIZE = words_vector1[i];
        }
    }
    
    /* count the number of documents N_DOCS (find max) */
    N_DOCS = 0;
    for (i=0; i<N_TOKENS; i++) {
        if (docs_vector1[i] > N_DOCS) {
            N_DOCS = docs_vector1[i];
        }
    }
    
    /* allocate memory */
    topics_vector  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    docs_vector  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    words_vector  = (int *) mxCalloc(N_TOKENS, sizeof(int));
    
    docs_counts  = (int *) mxCalloc(N_TOPICS*N_DOCS, sizeof(int)); /* doc count matrix (non-sparse) */
    
    if (DISPLAY_OUTPUT==2) {
        mexPrintf("Internal Memory Allocation\n");
        mexPrintf("\tw,d,z,order indices combined = %d bytes\n", 4 * sizeof(int) * N_TOKENS);
        mexPrintf("\twords_counts (full) matrix = %d bytes\n", sizeof(int) * VOC_SIZE * N_TOPICS );
        mexPrintf("\tdocs_counts (full) matrix = %d bytes\n", sizeof(int) * N_DOCS * N_TOPICS );
    }
    
    /* copy over the word/doc/topic indices into internal format (indices starting from 0!)*/    
    for (i=0; i<N_TOKENS; i++) {
        topics_vector[i] = (int) topics_vector_in[i] - 1;
        words_vector[i] = (int) words_vector1[i] - 1;
        docs_vector[i] = (int) docs_vector1[i] - 1;
    }
    
    /* RUN THE SAMPLER */
    /* seeding */
    seedMT(1 + SEED * 2); /* seeding only works on odd numbers */
    
    gibbs_sampler_fixed_LDA(ALPHA, VOC_SIZE, N_TOPICS, N_DOCS, N_SWEEPS, DISPLAY_OUTPUT, N_TOKENS, docs_vector, words_vector, phi,/* Variables only for input */
            topics_vector, docs_counts); /* Variables for input and output */
    
    
    /* CONVERT THE OUTPUT */
    /* convert the full docs_counts matrix into a sparse matrix */
    nzmaxdp = 0;
    for (i=0; i<N_DOCS*N_TOPICS; i++) {
        if(docs_counts[i] > 0){
            nzmaxdp++;
        }
    }
    
    plhs[0] = mxCreateSparse(N_DOCS, N_TOPICS, nzmaxdp, mxREAL);
    tmpPr  = mxGetPr(plhs[0]);
    tmpIr = mxGetIr(plhs[0]);
    tmpJc = mxGetJc(plhs[0]);
    n = 0;
    for (j=0; j<N_TOPICS; j++) {
        tmpJc[j] = n;
        for (i=0; i<N_DOCS; i++) {
            c = (int) docs_counts[i*N_TOPICS + j];
            if (c > 0) {
                tmpPr[n] = c;
                tmpIr[n] = i;
                n++;
            }
        }
    }
    tmpJc[N_TOPICS] = n;
    
    /* create double matrix, and convert topics_vector from int to double (and shift to have value in 1..N_TOPICS) */
    plhs[1] = mxCreateDoubleMatrix(N_TOKENS, 1, mxREAL);
    topics_vector_out = mxGetPr(plhs[1]);
    for (i=0; i<N_TOKENS; i++){
        topics_vector_out[i] = (double) topics_vector[i] + 1;
    }
}
