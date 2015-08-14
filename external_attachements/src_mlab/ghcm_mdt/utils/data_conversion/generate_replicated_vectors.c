#include "mex.h"

/*
 * Replicate documents and words indices, in order to obtain the correct 
 * number of occurrences.
 *
 * See sp_occurrences_to_vectors.m 
 *
 * [docs_vector_out, words_vector_out] = generate_replicated_vectors(...
 * docs_vector_in, words_vector_in, occurs_vector_in, N_TOKENS) 
 *
 * INPUT
 *      docs_vector_in      N_NON_ZEROSx1 vector
 *      words_vector_in     N_NON_ZEROSx1 vector
 *      occurs_vector_in    N_NON_ZEROSx1 vector
 *      N_TOKENS            scalar
 *
 * OUTPUT
 *      docs_vector_out     N_TOKENSx1 vector
 *      words_vector_out    N_TOKENSx1 vector
 */

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]) {
    double *docs_vector_in, *words_vector_in, *occurs_vector_in;            
    double *docs_vector_out, *words_vector_out;
    int N_TOKENS, N_NON_ZEROS;
    int i, j, next_index, doc, word, n_occurs;
    

    /* check for proper number of arguments */
    if (nrhs != 4) {
        mexErrMsgTxt("4 input arguments required");
    } else if (nlhs != 2) {
        mexErrMsgTxt("2 output arguments required");
    }
    
    N_NON_ZEROS = mxGetM(prhs[0]);
    
    docs_vector_in = mxGetPr(prhs[0]);
    words_vector_in = mxGetPr(prhs[1]);
    occurs_vector_in = mxGetPr(prhs[2]);
    N_TOKENS = (int) mxGetScalar(prhs[3]);
    
    
    /* Create an m-by-n mxArray; you will copy existing data into it */
    plhs[0] = mxCreateNumericMatrix(N_TOKENS, 1, mxDOUBLE_CLASS, mxREAL);
    docs_vector_out = mxGetPr(plhs[0]);
    
    plhs[1] = mxCreateNumericMatrix(N_TOKENS, 1, mxDOUBLE_CLASS, mxREAL);
    words_vector_out = mxGetPr(plhs[1]);

    next_index = 0;
    for(i = 0; i < N_NON_ZEROS; i++){
        doc = docs_vector_in[i];
        word = words_vector_in[i];
        n_occurs = occurs_vector_in[i];
        
        for(j = 0; j < n_occurs; j++){
            docs_vector_out[next_index] = doc;
            words_vector_out[next_index] = word;
            next_index++;
        }
    }
}
