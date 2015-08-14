% ESTIMATE_ROBUST_PHI Estimate phi in a robust way
%
% [robust_phi, words_counts_avg] = estimate_robust_phi(...
%     words_vector, docs_vector, topics_vector, ALPHA, BETA, ...
%     N_SAMPLES_FOR_PHI)
% 
% LDA recall: phi describes the distribution of words in a topics, while
% theta represents the proportions of topics in a document.
%
% To obtain a robust estimator of phi, several samples are generated
% starting from the input topics assignment (topics_vector) and performing 
% one sweep with different random seed.
% It is therefore important that topics_vector has been taken after
% convergence of the Gibbs sampling (i.e. close to a mode).
% 
% N_SAMPLES_FOR_PHI precises the number of samples to combine. A small
% value will require less time but may be less robust.
%
% INPUT
%   words_vector        N_TOKENSx1 vector
%   docs_vector         N_TOKENSx1 vector
%   topics_vector       N_TOKENSx1 vector
%   ALPHA               scalar
%   BETA                scalar
%   N_SAMPLES_FOR_PHI   scalar, optional (default 10)
%
% OUTPUT
%   robust_phi          VOC_SIZExN_TOPICS matrix
%   words_counts_avg    VOC_SIZExN_TOPICS sparse matrix
function [robust_phi, words_counts_avg] = estimate_robust_phi(...
    words_vector, docs_vector, topics_vector, ALPHA, BETA, ...
    N_SAMPLES_FOR_PHI)

% Set default value if needed
if(~exist('N_SAMPLES_FOR_PHI', 'var'))
    N_SAMPLES_FOR_PHI = 10;
end

% Retrieve constants
VOC_SIZE = max(words_vector);
N_TOPICS = max(topics_vector);

% Take a sample after one iteration (they will be highly correlated, which is
% what we want)
N_SWEEPS = 1;
SHOW_LDA_DETAILS = 0;

% Compute an average of words_counts over several samples (perform one
% iteration with different seed every time)
words_counts_avg = zeros(VOC_SIZE, N_TOPICS);
for sample = 1:N_SAMPLES_FOR_PHI
    fprintf('Sampling for robust phi %d/%d\n', sample, N_SAMPLES_FOR_PHI);
    seed = sample;
    
    [words_counts, ~, ~] = ...
        gibbs_sampler_LDA(words_vector, docs_vector, N_TOPICS, ...
        N_SWEEPS , ALPHA , BETA , seed , SHOW_LDA_DETAILS, topics_vector);
    
    words_counts_avg = words_counts_avg + words_counts;
end
words_counts_avg = words_counts_avg / N_SAMPLES_FOR_PHI;

% From the average of words_counts matrices, compute robust_phi
robust_phi = estimate_phi(words_counts_avg, BETA);

end
