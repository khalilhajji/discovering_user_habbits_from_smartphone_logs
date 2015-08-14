% [docs_counts, topics_vector_out] = gibbs_sampler_fixed_LDA(...
%   words_vector, docs_vector, N_TOPICS, N_SWEEPS, ALPHA, ...
%   SEED, DISPLAY_OUTPUT, topics_vector_in, phi)
% 
% Similarly to gibbs_sampler_LDA, this method allows to sample topics
% assignments for a given dataset, but with a fixed topic structure phi
% (i.e. we should obtain a sample of p(z|w, phi, alpha)).
% 
% See also gibbs_sampler_LDA
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
%   phi                 VOC_SIZE x N_TOPICS matrix
% 
% OUTPUT
%   docs_counts         N_DOCS   x N_TOPICS matrix
%   topics_vector_out   N_TOKENS x 1 vector
