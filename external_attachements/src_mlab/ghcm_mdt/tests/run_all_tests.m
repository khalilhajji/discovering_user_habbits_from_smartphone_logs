% To run all tests, make sure you are in the test directory and run this script

% Add the whole toolbox to the path (to know where tests are, however tests
% must load the path themself)
addpath(genpath('.'))

%% Tests for utils
runtests test_synthetic_data_generator

%% 
runtests test_utils

%% Tests for LDA fitting
runtests test_LDA_fitting_small_functions

%%
runtests test_gibbs_sampler_LDA

%%
runtests test_gibbs_sampler_fixed_LDA