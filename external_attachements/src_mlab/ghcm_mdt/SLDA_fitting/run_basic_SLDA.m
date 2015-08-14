% RUN_BASIC_SLDA Produces SLDA samples using Gibbs sampling
% 
% Perform sampling on the sp_occurrences matrices, for a  SLDA model with
% parameters n_topics, alpha and beta. n_samples samples are written in
% output_path, with the first sample taken after burnin_period sampling
% iterations, and the following samples taken every thinning_period
% sampling iterations.
% 
% INPUT
%   sp_occurrences: TxD sparse matrix
%   output_path: string
%   n_topics, alpha, beta: scalar
%   burnin_period, thinning_period, n_samples: scalar
% 
%   rated_docs: 1xD boolean vector
%   ratings: 1xD double vector
function run_basic_SLDA(sp_occurrences, output_path, ...
    n_topics, alpha, beta, ...
    burnin_period, thinning_period, n_samples, ...
    rated_docs, ratings, SIGMA2, SEED)

SHOW_LDA_DETAILS = 1; % To show some details

% First convert occurrences matrix to vectors by repeating
[docs_vector, terms_vector] = sp_occurrences_to_vectors(sp_occurrences);

n_tokens = length(docs_vector);

% Create the output directory
mkdir(output_path);

% Generate random initial topics (usually denoted by z)
if(~exist('SEED', 'var'))
    SEED = 1; % If the function has been called without a seed
end
rng(SEED);
topics_vector = randi(n_topics, 1, n_tokens);

% Initialize ratings parameters
eta = zeros(1, n_topics);
sigma = 1;

% Run the sampling inference algorithm

sample = find_sample_to_start_with(output_path);
if(sample > 1) % Allows to restart an aborted training
    SLDA_output_filename = get_SLDA_output_filename(output_path, sample-1);
    load(SLDA_output_filename);
end

while(sample <= n_samples)
    tic
    seed = sample; % Need to be changed every time
    
    if(sample == 1)
        n_sampling_steps = burnin_period;
    else
        n_sampling_steps = thinning_period;
    end
    
    fprintf('# Sampling\n');
    [term_topic_counts, doc_topic_counts, topics_vector] = ...
        gibbs_sampler_SLDA(terms_vector, docs_vector, n_topics, ...
        n_sampling_steps , alpha , beta , seed , SHOW_LDA_DETAILS, topics_vector, ...
        rated_docs, ratings, eta, sigma);
    
    fprintf('# Optimize params\n')
    if(sum(rated_docs) ~= 0)
        [eta, sigma] = optimize_params(rated_docs, ratings, doc_topic_counts);
    end
    
    fprintf('# Computing estimates for topics distributions and topics proportions\n');
    [topics_distribs, topics_props] = compute_estimates(...
        term_topic_counts, doc_topic_counts, alpha, beta);
   
    fprintf('# Saving sample\n')
    SLDA_output_filename = sprintf([output_path 'output_SLDA_sample%d.mat'], sample);
    save(SLDA_output_filename, 'n_topics', 'alpha', 'beta', ...
        'topics_distribs', 'topics_props', 'topics_vector', ...
        'burnin_period', 'thinning_period', 'n_samples', ...
        'rated_docs', 'ratings', 'eta', 'sigma', ...
        '-v7.3');
    toc
    
    sample = sample + 1;
end

end

function SLDA_output_filename = get_SLDA_output_filename(output_path, sample)
SLDA_output_filename = sprintf([output_path 'output_SLDA_sample%d.mat'], sample);
end

function sample = find_sample_to_start_with(output_path)
sample = 1;
while(exist(get_SLDA_output_filename(output_path, sample), 'file'))
    sample = sample + 1;
end
end

