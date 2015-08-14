% ESTIMATE_ROBUST_THETA Estimate theta in a robust way for fixed phi
% 
% [robust_theta, docs_counts_avg] = estimate_robust_theta(...
%     words_vector, docs_vector, topics_vector, ALPHA, ...
%     phi, N_SAMPLES_FOR_THETA, BURNIN_PERIOD)
% 
% LDA recall: phi describes the distribution of words in a topics, while
% theta represents the proportions of topics in a document.
% 
% To obtain a robust estimator of theta, several samples are generated
% starting from the input topics assignment (topics_vector) and performing 
% BURNIN_PERIOD sweeps with different random seed, while keeping the topics
% structure fixed (phi).
% It is therefore important that topics_vector and phi have been taken after
% convergence of the Gibbs sampling (i.e. close to a mode).
% 
% N_SAMPLES_FOR_PHI is the number of samples to combine. A small value will 
% require less time but may be less robust.
% 
% BURNIN_PERIOD is the number of sweeps to perform before taking a sample.
% A large value value allow to have a estimator of theta independent of
% the initial topics_vector (given phi).
% 
% See also ESTIMATE_ROBUST_PHI to obtain a good phi for input.
% 
% INPUT
%   words_vector        N_TOKENSx1 vector
%   docs_vector         N_TOKENSx1 vector
%   topics_vector       N_TOKENSx1 vector
%   ALPHA               scalar
%   phi                 N_WORDSxN_TOPICS matrix
%   N_SAMPLES_FOR_THETA  scalar, optional (default: 10)
%   BURNIN_PERIOD       scalar, optional (default: 5)
% 
% OUTPUT
%   robust_theta        N_TOPICSxN_DOCS matrix
%   docs_counts_avg     N_DOCSxN_TOPICS sparse matrix
function [robust_theta, docs_counts_avg] = estimate_robust_theta(...
    words_vector, docs_vector, topics_vector, ALPHA, ...
    phi, N_SAMPLES_FOR_THETA, BURNIN_PERIOD)

SHOW_LDA_DETAILS = 0;

% Use many samples to have a good approximation
if(~exist('N_SAMPLES_FOR_THETA', 'var'))
    N_SAMPLES_FOR_THETA = 10; 
end

% Take a sample after many iterations, so that samples are approx.
% independent
if(~exist('BURNIN_PERIOD', 'var'))
    BURNIN_PERIOD = 5; 
end

% Retrieve constants
N_DOCS = max(docs_vector);
N_TOPICS = max(topics_vector);

% Compute an average of words_counts over (approx. independent) samples
docs_counts_avg = zeros(N_DOCS, N_TOPICS);
for sample = 1:N_SAMPLES_FOR_THETA
    fprintf('Sampling for robust theta %d/%d\n', sample, N_SAMPLES_FOR_THETA);
    seed = sample;
    
    % Start sampling every time from topics_vector
    [docs_counts, ~] = ...
        gibbs_sampler_fixed_LDA(words_vector, docs_vector, N_TOPICS, ...
        BURNIN_PERIOD , ALPHA , seed , SHOW_LDA_DETAILS, topics_vector, phi);
    
    docs_counts_avg = docs_counts_avg + docs_counts;
end
docs_counts_avg = docs_counts_avg / N_SAMPLES_FOR_THETA;

robust_theta = estimate_theta(docs_counts_avg, ALPHA);

end
