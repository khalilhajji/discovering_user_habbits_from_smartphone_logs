% Tests for gibbs_sampler_fixed_LDA functions
%
% These tests can be launch with the command 'runtests'
function tests = test_gibbs_sampler_fixed_LDA
% test_check_p_z_given_w_phi_sum(0)
tests = functiontests(localfunctions);
end

function setupOnce(testCase) %#ok<INUSD,DEFNU>
addpath(genpath('../../LDA_fitting'))
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Test the limit behavior when documents can have only one topic 
% => shouldn't change state
function test_sampling(testCase) %#ok<DEFNU>
N_TOPICS = 2;
N_SWEEPS = 10;
ALPHA = 1e-10;
SEED = 1;
SHOW_LDA_DETAILS = 0;

docs_vector =   [1 1 1 2 2 2]';
words_vector =  [1 1 1 2 2 2]';
topics_vector = [1 1 1 2 2 2]';
phi = [0.3 0.2; 0.7 0.8];

expected_docs_counts = sparse([3 0; 0 3]);
expected_topics_vector = topics_vector;

[output_docs_counts, output_topics_vector] = ...
    gibbs_sampler_fixed_LDA(words_vector, docs_vector, N_TOPICS, ...
    N_SWEEPS , ALPHA , SEED , SHOW_LDA_DETAILS, topics_vector, phi);

verifyEqual(testCase, output_docs_counts, expected_docs_counts);
verifyEqual(testCase, output_topics_vector, expected_topics_vector);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MORE ADVANCED
% Test whether on a very simple model, the ratio of observed 
% configuration z tends to its expected value p(z|w, phi)
function test_sampling3(testCase) %#ok<DEFNU>
N_TOPICS = 2;
N_SWEEPS = 20; % Must be large enough to reach stable regime 
ALPHA = 0.1;
BETA = 0.1;
SHOW_LDA_DETAILS = 0;

docs_vector =   [1 1 1 2 2]'; % 2 docs
words_vector =  [1 1 2 2 2]'; % 2 words
phi = [0.3 0.2; 0.7 0.8];

N_DOCS = 2;
VOC_SIZE = 2;
N_TOKENS = length(docs_vector);

% Compute the probabilities p(z|w) for all z
topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);
N_TOPICS_VECTORS = N_TOPICS^N_TOKENS;
probas = zeros(1, N_TOPICS_VECTORS);
for i = 1:N_TOPICS_VECTORS
    probas(i) = compute_p_z_given_w_phi(...
        words_vector, docs_vector, topics_vectors(:,i), phi, ...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
end

% Fit many times the model (and take a sample after enough iterations)
% => Counts how many time each possible topics_vector has been sampled
topics_vectors_counts = zeros(1, N_TOPICS_VECTORS); 
N = 1e4;
for n = 1:N
    SEED = n;
    init_topics_vector = randi(N_TOPICS, N_TOKENS, 1);
    
    [~, output_topics_vector] = ...
        gibbs_sampler_fixed_LDA(words_vector, docs_vector, N_TOPICS, ...
        N_SWEEPS , ALPHA , SEED , SHOW_LDA_DETAILS, init_topics_vector, phi);
    
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
% Test for p_z_given_w_phi, used for the previous test
% Check that p(z|w, phi) sum to one over all possible z
function test_check_p_z_given_w_phi_sum(testCase) %#ok<DEFNU>
docs_vector = [1 1 2 2]';
words_vector = [1 2 2 2]';
phi = [0.3 0.2; 0.7 0.8];
N_DOCS = 2;
VOC_SIZE = 2;
N_TOPICS = 2;
ALPHA = 0.1;
BETA = 0.1;

N_TOKENS = length(docs_vector);

topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);

p_z_given_w_phi_sum = 0;
for i = 1:size(topics_vectors, 2)
    p_z_given_w_phi = compute_p_z_given_w_phi(...
        words_vector, docs_vector, topics_vectors(:,i), phi, ...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
    
    p_z_given_w_phi_sum = p_z_given_w_phi_sum + p_z_given_w_phi;
end

verifyEqual(testCase, abs(p_z_given_w_phi_sum-1)<1e-10, true); % Must sum to one
end
