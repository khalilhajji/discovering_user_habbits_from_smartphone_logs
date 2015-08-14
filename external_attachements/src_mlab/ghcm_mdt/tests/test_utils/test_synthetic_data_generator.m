% Tests for synthetic data generator functions
% 
% These tests can be launch with the command 'runtests'
function tests = test_synthetic_data_generator
tests = functiontests(localfunctions);
end

function setupOnce(testCase) %#ok<INUSD,DEFNU>
% Add LDA toolbox path
addpath(genpath('../../utils/synthetic_data_generator'))
end

function test_rand_categorical(testCase) %#ok<DEFNU>
% According to the law of large number, if we have enough samples then the
% observed average should be close to the expected value.
%
% Take Xi ~ rand_categorical([1/6 5/6]) and verify that their average is
% close to E[Xi]=1/6*1+5/6*2=11/6

PRECISION = 1e-2; % Set so that it doesn't need too much samples (=> time)
PROBAS = [1/6 5/6];
EXPECTED_VALUE = 11/6;

N = 1e4;

mean_Xis = 0;
for n = 1:N
    [Xi] = rand_categorical(PROBAS);
    mean_Xis = mean_Xis + Xi;
end
mean_Xis = mean_Xis / N;

% This test should pass with high probability (relaunch it a second time if
% it fails).
verifyEqual(testCase, abs(mean_Xis - EXPECTED_VALUE) <= PRECISION, true);
end

function test_rand_dirichlet(testCase) %#ok<DEFNU>
% According to the law of large number, if we have enough samples then the
% observed average should be close to the expected value.
%
% Take thetai ~ rand_dirichlet(0.1, n_dim=3) and verify that their average is
% close to E[thetai] = [1/3 1/3 1/3]'

PRECISION = 5e-2; % Set so that it doesn't need too much samples (=> time)
N_SIMULTANEOUS_SAMPLES = 1;
N_DIM = 3;
ALPHA = 1/10;
EXPECTED_VALUE = [1/3 1/3 1/3]';

N = 1e3;

mean_thetais = 0;
for n = 1:N
    [thetai] = rand_dirichlet(N_SIMULTANEOUS_SAMPLES, N_DIM, ALPHA);
    mean_thetais = mean_thetais + thetai;
end
mean_thetais = mean_thetais / N;

% This test should pass with high probability (relaunch it a second time if
% it fails).
verifyEqual(testCase, max(abs(mean_thetais - EXPECTED_VALUE)) <= PRECISION, true);

end

function test_generate_synthetic_dataset(testCase) %#ok<DEFNU>
% Test various assumptions (sizes, content of vector / mean of content
FILENAME = 'tmp.mat';
ALPHA = 0.1;
BETA = 0.1;
Nd = 2;
N_DOCS = 3;
N_TOPICS = 4;
VOC_SIZE = 5;

% Check generated sizes
generate_synthetic_dataset(FILENAME, ALPHA, BETA, Nd, N_DOCS, N_TOPICS, VOC_SIZE)

load(FILENAME, 'phi', 'theta', 'words_vector', 'docs_vector', 'topics_vector');

verifyEqual(testCase, size(phi), [VOC_SIZE, N_TOPICS]);
verifyEqual(testCase, size(theta), [N_TOPICS, N_DOCS]);
verifyEqual(testCase, size(words_vector), [N_DOCS*Nd 1]);
verifyEqual(testCase, size(docs_vector), [N_DOCS*Nd 1]);
verifyEqual(testCase, size(topics_vector), [N_DOCS*Nd 1]);

% Check that docs_vector contains 2 times each doc
verifyEqual(testCase, sort(docs_vector), sort(repmat(1:N_DOCS, 1, Nd))');

% Check whether mean values of words_vector and topics_vector are close to
% expected mean.
N = 50;
PRECISION = 0.4;

mean_words_vector_mean = 0;
mean_topics_vector_mean = 0;
for n = 1:N
    generate_synthetic_dataset(FILENAME, ALPHA, BETA, Nd, N_DOCS, N_TOPICS, VOC_SIZE)
    
    load(FILENAME, 'words_vector', 'topics_vector');
    
    mean_words_vector_mean = mean_words_vector_mean + mean(words_vector);
    mean_topics_vector_mean = mean_topics_vector_mean + mean(topics_vector);
end
mean_words_vector_mean = mean_words_vector_mean / N;
mean_topics_vector_mean = mean_topics_vector_mean / N;

verifyEqual(testCase, abs(mean_words_vector_mean - mean(1:VOC_SIZE)) <= PRECISION, true);
verifyEqual(testCase, abs(mean_topics_vector_mean - mean(1:N_TOPICS)) <= PRECISION, true);

delete(FILENAME)

end
