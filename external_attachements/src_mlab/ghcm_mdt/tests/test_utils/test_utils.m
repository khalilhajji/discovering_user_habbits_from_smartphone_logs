% Tests for utils functions
% 
% These tests can be launch with the command 'runtests'
function tests = test_utils
tests = functiontests(localfunctions);
end

function setupOnce(testCase) %#ok<INUSD,DEFNU>
% Add LDA toolbox path
addpath(genpath('../../utils'))
end

function test_sp_occurrences_to_vectors(testCase) %#ok<DEFNU>
sp_occurrences = sparse([1 0 2 0; ...
                         0 1 0 0; ...
                         0 0 0 1]); 

[docs_vector, words_vector] = sp_occurrences_to_vectors(sp_occurrences);

verifyEqual(testCase, docs_vector, [1 2 3 3 4]');
verifyEqual(testCase, words_vector, [1 2 1 1 3]');
end
