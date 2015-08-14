% Tests for gibbs_sampler_LDA functions
%
% These tests can be launch with the command 'runtests'
function tests = test_gibbs_sampler_LDA
tests = functiontests(localfunctions);
end

function setupOnce(testCase) %#ok<INUSD,DEFNU>
addpath(genpath('../../LDA_fitting'))
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Test the limit behavior when documents can have only one topic and topics
% can have only one word => shouldn't change state
function test_sampling(testCase) %#ok<DEFNU>
N_TOPICS = 2;
N_SWEEPS = 10;
ALPHA = 1e-10;
BETA = 1e-10;
SEED = 1;
SHOW_LDA_DETAILS = 0;

docs_vector =   [1 1 1 2 2 2]';
words_vector =  [1 1 1 2 2 2]';
topics_vector = [1 1 1 2 2 2]';

expected_words_counts = sparse([3 0; 0 3]);
expected_docs_counts = sparse([3 0; 0 3]);
expected_topics_vector = topics_vector;

[output_words_counts, output_docs_counts, output_topics_vector] = ...
    gibbs_sampler_LDA(words_vector, docs_vector, N_TOPICS, ...
    N_SWEEPS , ALPHA , BETA , SEED , SHOW_LDA_DETAILS, topics_vector);

verifyEqual(testCase, output_words_counts, expected_words_counts);
verifyEqual(testCase, output_docs_counts, expected_docs_counts);
verifyEqual(testCase, output_topics_vector, expected_topics_vector);
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Test the limit behavior when documents should have uniform distribution
% over topics and topics should have uniform distribution over words
% (i.e. by taking alpha and beta very large)
function test_sampling2(testCase) %#ok<DEFNU>
N_TOPICS = 2;
N_SWEEPS = 10;
ALPHA = 1e10;
BETA = 1e10;
SHOW_LDA_DETAILS = 0;

docs_vector =   [1 1 1 2 2 2]'; % 2 docs
words_vector =  [1 1 1 2 2 2]'; % 2 words
topics_vector = [1 1 1 2 2 2]'; % 2 topics

expected_words_counts = sparse([1.5 1.5; 1.5 1.5]);
expected_docs_counts = sparse([1.5 1.5; 1.5 1.5]);
expected_topics_vector = [1.5 1.5 1.5 1.5 1.5 1.5]';

mean_words_counts = zeros(2, 2);
mean_docs_counts = zeros(2, 2);
N_TOKENS = 6;
mean_topics_vector = zeros(N_TOKENS, 1);

N = 1e4;
for n = 1:N
    SEED = n;
    
    [output_words_counts, output_docs_counts, output_topics_vector] = ...
        gibbs_sampler_LDA(words_vector, docs_vector, N_TOPICS, ...
        N_SWEEPS , ALPHA , BETA , SEED , SHOW_LDA_DETAILS, topics_vector);
    
    mean_words_counts = mean_words_counts + output_words_counts;
    mean_docs_counts = mean_docs_counts + output_docs_counts;
    mean_topics_vector = mean_topics_vector + output_topics_vector;
end
mean_words_counts = mean_words_counts/N;
mean_docs_counts = mean_docs_counts/N;
mean_topics_vector = mean_topics_vector/N;

PRECISION = 0.2;
verifyEqual(testCase, sum(sum(abs(expected_words_counts-mean_words_counts))) < PRECISION, true);
verifyEqual(testCase, sum(sum(abs(expected_docs_counts-mean_docs_counts))) < PRECISION, true);
verifyEqual(testCase, sum(abs(expected_topics_vector-mean_topics_vector)) < PRECISION, true);
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MORE ADVANCED
% Test whether on a very simple model, the ratio of observed 
% configuration z tends to its expected value p(z|w)
function test_sampling3(testCase) %#ok<DEFNU>
N_TOPICS = 2;
N_SWEEPS = 20; % Must be large enough to reach stable regime 
ALPHA = 0.1;
BETA = 0.1;
SHOW_LDA_DETAILS = 0;

docs_vector =   [1 1 1 2 2]'; % 2 docs
words_vector =  [1 1 2 2 2]'; % 2 words
N_DOCS = 2;
VOC_SIZE = 2;
N_TOKENS = length(docs_vector);

% Compute the probabilities p(z|w) for all z
topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);
N_TOPICS_VECTORS = N_TOPICS^N_TOKENS;
probas = zeros(1, N_TOPICS_VECTORS);
for i = 1:N_TOPICS_VECTORS
    probas(i) = compute_p_z_given_w(words_vector, docs_vector, topics_vectors(:,i), ...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
end

% Fit many times the model (and take a sample after enough iterations)
% => Counts how many time each possible topics_vector has been sampled
topics_vectors_counts = zeros(1, N_TOPICS_VECTORS); 
N = 1e4;
for n = 1:N
    SEED = n;
    init_topics_vector = randi(N_TOPICS, N_TOKENS, 1);
    
    [~, ~, output_topics_vector] = ...
        gibbs_sampler_LDA(words_vector, docs_vector, N_TOPICS, ...
        N_SWEEPS , ALPHA , BETA , SEED , SHOW_LDA_DETAILS, init_topics_vector);
    
    % Find and increment the count corresponding to the sampled vector
    topics_vector_index = ...
        find(sum(abs(bsxfun(@minus, topics_vectors, output_topics_vector)), 1)==0);
    topics_vectors_counts(topics_vector_index) = ...
        topics_vectors_counts(topics_vector_index) + 1;
end

PRECISION = 0.05; % Can be arbitrarly small if enough samples
% Check that the observed propotions and the expected probas are close
verifyEqual(testCase, sum(abs(topics_vectors_counts/N - probas)) < PRECISION, true);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Test for p_z_given_w, used for the previous test
% Check that p(z|w) sum to one over all possible z
function test_check_p_z_given_w_sum(testCase) %#ok<DEFNU>
docs_vector = [1 1 2 2]';
words_vector = [1 2 2 2]';
N_DOCS = 2;
VOC_SIZE = 2;
N_TOPICS = 2;
ALPHA = 0.1;
BETA = 0.1;

N_TOKENS = length(docs_vector);

topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);

p_z_given_w_sum = 0;
for i = 1:size(topics_vectors, 2)
    p_z_given_w = compute_p_z_given_w(...
        words_vector, docs_vector, topics_vectors(:,i), ...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
    
    p_z_given_w_sum = p_z_given_w_sum + p_z_given_w;
end

verifyEqual(testCase, abs(p_z_given_w_sum-1)<1e-10, true); % Must sum to one
end
