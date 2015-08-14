% This function uses a topic structure already trained on main data to attribute 
% topics to new documents.
%
% fit_new_data(docs_vector_new, words_vector_new, docs_vector_old, words_vector_old, ...
%     INPUT_MAIN_FILENAME, OUTPUT_NEW_FILENAME, N_SWEEPS)
%
% Starting from existing fitted data (described by docs_vector_old, words_vector_old, 
% and topics_vector contained in INPUT_MAIN_FILENAME), topics are sampled
% for new documents (which results in an updated topic structure phi, and
% topic proportions for the new documents).
% 
% Note that values in docs_vector_new must range in {1, ... N_TOKENS_NEW}
% Note that values in docs_vector_old must range in {1, ... N_TOKENS_OLD}
% Note that values in words_vector_new AND words_vector_old must range in
% {1, ... VOC_SIZE}
% 
% A sample is saved in OUTPUT_FILENAME. Its most important variables are:
% - topics_vector   N_TOKENS_NEW x 1 vector, topic assigned to each (new) token
% - phi             VOC_SIZE x N_TOPICS matrix, words distributions by topic
% - theta           N_TOPICS x N_DOCS_NEW matrix, topics distributions by 
%                   document, only for new documents
%
% INPUT
%   docs_vector_new         N_TOKENS_NEWx1 vector
%   words_vector_new        N_TOKENS_NEWx1 vector
%   docs_vector_old         N_TOKENS_OLDx1 vector
%   words_vector_old        N_TOKENS_OLDx1 vector
%   INPUT_MAIN_FILENAME     string
%   OUTPUT_NEW_FILENAME     string
%   [N_SWEEPS]              scalar, optional (default: 200)
function fit_new_data(docs_vector_new, words_vector_new, docs_vector_old, words_vector_old, ...
    INPUT_MAIN_FILENAME, OUTPUT_NEW_FILENAME, N_SWEEPS)

% Load the trained topic structure (phi) and uses the same parameters
load(INPUT_MAIN_FILENAME, 'topics_vector', 'PARAMS');
topics_vector_old = topics_vector; %#ok<NODEF>

N_TOPICS = PARAMS.N_TOPICS;
ALPHA = PARAMS.ALPHA;
BETA = PARAMS.BETA;

% Default value if needed
if(~exist('N_SWEEPS', 'var'))
    N_SWEEPS = 200;
end
DISPLAY_OUTPUT = 1;
SEED = 1;

N_TOKENS_NEW = length(docs_vector_new);
N_DOCS_NEW = max(docs_vector_new);

% Randomly assign topics for new documents
topics_vector_new = randi(N_TOPICS, N_TOKENS_NEW, 1);

% Merge old and new vectors
words_vector_all = [words_vector_new; words_vector_old];
docs_vector_all = [docs_vector_new; docs_vector_old + N_DOCS_NEW]; % Shift docs indexing
topics_vector_all = [topics_vector_new; topics_vector_old];

% Run the sampling without resampling old tokens
tokens_to_sample = 1:N_TOKENS_NEW;

fprintf('# Sampling topics for new data\n')
[words_counts_all, docs_counts_all, topics_vector_all] = gibbs_sampler_LDA(...
    words_vector_all, docs_vector_all, N_TOPICS, N_SWEEPS, ALPHA, BETA, ...
    SEED, DISPLAY_OUTPUT, topics_vector_all, tokens_to_sample);

% Estimate phi and theta, and extract topic_vector for only new docs
fprintf('# Estimating phi and theta for new data\n')
phi = estimate_phi(words_counts_all, BETA); %#ok<*NASGU>

docs_counts_new = docs_counts_all(1:N_DOCS_NEW,:);
theta = estimate_theta(docs_counts_new, ALPHA);

topics_vector = topics_vector_all(1:N_TOKENS_NEW);

% Save
fprintf('# Saving\n')
save(OUTPUT_NEW_FILENAME, ...
    'phi', 'theta', 'topics_vector', ...
    'N_TOPICS', 'ALPHA', 'BETA', 'N_SWEEPS', '-v7.3');

end
