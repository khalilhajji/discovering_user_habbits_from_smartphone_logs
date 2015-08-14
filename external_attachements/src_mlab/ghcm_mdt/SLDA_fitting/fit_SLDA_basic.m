% TODO document
%
% FIT_SLDA_BASIC Produces SLDA samples using Gibbs sampling
%
% [phi, theta] = fit_SLDA_basic(docs_vector, words_vector, rated_docs, ratings, ...
%     N_TOPICS, ALPHA, BETA, N_SWEEPS_PER_ITER, MAX_ITERS, SEED, topics_vector)
%
% INPUT
%   docs_vector         N_TOKENS x 1 vector
%   words_vector        N_TOKENS x 1 vector
%   rated_docs          N_DOCS x 1 vector
%   ratings             N_DOCS x 1 vector
%   N_TOPICS            scalar
%   ALPHA               scalar
%   BETA                scalar
%   N_SWEEPS_PER_ITER 	scalar
%   MAX_ITERS         	scalar
%   SEED                scalar, optional (default: 1)
%   topics_vector       N_TOKENS x 1 vector (default: <random using SEED>)
% 
% OUTPUT
%   phi                 N_WORDS x N_TOPICS matrix   
%   theta               N_TOPICS x N_DOCS matrix   
function [phi, theta] = fit_SLDA_basic(docs_vector, words_vector, rated_docs, ratings, ...
    N_TOPICS, ALPHA, BETA, N_SWEEPS_PER_ITER, MAX_ITERS, SEED, topics_vector)

SHOW_LDA_DETAILS = 1; % To show some details

N_TOKENS = length(docs_vector);

% Generate a random topic assignment if not given in input
if(~exist('topics_vector', 'var'))
    % Use a fixed seed if it is not given in input
    if(~exist('SEED', 'var'))
        SEED = 1; % If the function has been called without a seed
    end
    rng(SEED);
    
    topics_vector = randi(N_TOPICS, 1, N_TOKENS);
end

% Initialize ratings parameters
eta = zeros(1, N_TOPICS);
sigma = 1;

% Run the sampling inference algorithm
iters_done = 0;
while(iters_done <= MAX_ITERS)
    tic
    seed = iters_done; % Need to be changed every time
    
    fprintf('# Sampling\n');
    [words_counts, docs_counts, topics_vector] = ...
        GibbsSamplerSLDA(words_vector, docs_vector, N_TOPICS, ...
        N_SWEEPS_PER_ITER , ALPHA , BETA , seed , SHOW_LDA_DETAILS, topics_vector, ...
        rated_docs, ratings, eta, sigma);
    
    fprintf('# Optimize params\n')
    if(sum(rated_docs) ~= 0)
        [eta, sigma] = optimize_params(rated_docs, ratings, docs_counts);
    end
    toc
    
    iters_done = iters_done + 1;
end


fprintf('# Computing estimates for theta\n');

phi = estimate_phi(words_counts, BETA);
theta = estimate_theta(docs_counts, ALPHA);

end


