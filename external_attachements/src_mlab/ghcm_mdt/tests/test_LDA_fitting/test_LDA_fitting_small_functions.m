% Tests for LDA fitting functions:
% - compute_counts
% - estimate_phi
% - estimate_theta
%
% These tests can be launch with the command 'runtests'
function tests = test_LDA_fitting_small_functions
tests = functiontests(localfunctions);
end

function setupOnce(testCase) %#ok<INUSD,DEFNU>
addpath(genpath('../../LDA_fitting'))
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function test_compute_counts(testCase) %#ok<DEFNU>
words_vector =  [1 2 1 3 4 2]';
docs_vector =   [1 1 1 2 2 2]';
topics_vector = [2 2 2 1 1 1]';
N_TOPICS = 2;

[words_counts, docs_counts] = compute_counts(words_vector, docs_vector, topics_vector, N_TOPICS);

expected_words_counts = sparse(...
    [0 2; ...
    1 1; ...
    1 0; ...
    1 0]);
expected_docs_counts = sparse(...
    [0 3; ...
    3 0]);

verifyEqual(testCase, words_counts, expected_words_counts);
verifyEqual(testCase, docs_counts, expected_docs_counts);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function test_estimate_phi(testCase) %#ok<DEFNU>
words_counts = sparse(...
    [1 0;
    0 1;
    1 1;
    0 0]);

BETA = 0; % Test limit case

phi = estimate_phi(words_counts, BETA);

expected_phi = ...
    [0.5 0; ...
    0   0.5; ...
    0.5 0.5; ...
    0   0];

verifyEqual(testCase, phi, expected_phi);

end

function test_estimate_phi2(testCase) %#ok<DEFNU>
words_counts = sparse(...
    [1 0;
    0 1;
    1 1;
    0 0]);

BETA = 1e10; % Test limit case

phi = estimate_phi(words_counts, BETA);

expected_limit_phi = ...
    [0.25 0.25; ...
    0.25 0.25; ...
    0.25 0.25; ...
    0.25 0.25];

PRECISION = 1e-3;

verifyEqual(testCase, sum(sum(abs(phi-expected_limit_phi))) < PRECISION, true);

end

function test_estimate_phi3(testCase) %#ok<DEFNU>
words_counts = sparse(...
    [1 0 1; ...
     0 0 1]);

BETA = 0; % Test limit case

phi = estimate_phi(words_counts, BETA);

expected_phi = ...
    [1 0.5  0.5; ...
    0  0.5  0.5];

verifyEqual(testCase, phi, expected_phi);

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function test_estimate_theta(testCase) %#ok<DEFNU>
docs_counts = sparse(...
    [1 0; ...
    0 1; ...
    1 1; ...
    2 2]);

ALPHA = 0; % Test limit case

theta = estimate_theta(docs_counts, ALPHA);

expected_theta = ...
    [1 0 0.5 0.5; ...
    0  1 0.5 0.5];

verifyEqual(testCase, theta, expected_theta);

end

function test_estimate_theta2(testCase) %#ok<DEFNU>
docs_counts = sparse(...
    [1 0; ...
    0 1; ...
    1 1; ...
    2 2]);

ALPHA = 1e10; % Test limit case

theta = estimate_theta(docs_counts, ALPHA);

expected_limit_theta = ...
    [0.5 0.5 0.5 0.5; ...
    0.5 0.5 0.5 0.5];

PRECISION = 1e-3;

verifyEqual(testCase, sum(sum(abs(theta-expected_limit_theta))) < PRECISION, true);

end
