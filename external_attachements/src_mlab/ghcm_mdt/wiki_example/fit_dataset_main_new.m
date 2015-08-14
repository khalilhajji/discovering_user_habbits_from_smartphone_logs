% ### PART 3 ###
% 
% Show how to use a fitted model on new data
% 1) Fit the model on 'main' data
% 2) Use it to infer topic of 'new' data 

%% Start by adding neccessary folder of the LDA_toolbox to the path 
addpath(genpath('../utils')); 
addpath('../LDA_fitting'); 

%% Load the data, split randomly 'main' and 'new', and convert to vector format
INPUT_FILE = 'wiki_toy_dataset5.mat';
load(INPUT_FILE);

% Randomly assign docs either to main data or to new data
PERCENTAGE_MAIN = 0.9; % Can also work with much smaller values, e.g. 0.5;
rng(1); docs_permutation = randperm(N_DOCS); % Same seed for consistance
docs_main_data = docs_permutation(1:floor(PERCENTAGE_MAIN*N_DOCS));
docs_new_data = docs_permutation(ceil(PERCENTAGE_MAIN*N_DOCS):end);

sp_occurrences_main = sp_occurrences(:, docs_main_data);
sp_occurrences_new = sp_occurrences(:, docs_new_data);

% Reduce the vocabulary, so that we only use words present in the main data
words_in_main = find(sum(sp_occurrences_main,2)~=0);
sp_occurrences_main = sp_occurrences_main(words_in_main,:);
sp_occurrences_new = sp_occurrences_new(words_in_main,:);

% Convert to vector format
[docs_vector_main, words_vector_main] = sp_occurrences_to_vectors(sp_occurrences_main);
[docs_vector_new, words_vector_new] = sp_occurrences_to_vectors(sp_occurrences_new);

%% Fit the LDA model to main data
MAIN_FILENAME = 'lda_output_main.mat';

PARAMS.N_TOPICS = 5;
PARAMS.MAX_ITERS = 10; % Enough for a small dataset

fit_LDA_advanced(docs_vector_main, words_vector_main, MAIN_FILENAME, PARAMS)

%% Fit the new data with the previous structure 
NEW_FILENAME = 'lda_output_new.mat';

fit_new_data(docs_vector_new, words_vector_new, docs_vector_main, words_vector_main,...
    MAIN_FILENAME, NEW_FILENAME)

%% Perform classification into clusters of 'main' data, and compare to original topics
load(MAIN_FILENAME, 'theta')

[~, docs_most_likely_topics] = max(theta, [], 1);

% Display a matrix where the count in entry (i,j) is the number of document
% with original topic i and LDA-found topic j.
% Note that topics found by LDA are unordered by nature.
% Note that we need to filter and reorder documents in sp_topics.
N_DOCS_MAIN = length(docs_main_data);
sp_topics_found = sparse(docs_most_likely_topics, 1:N_DOCS_MAIN, ones(1, N_DOCS_MAIN));
main_topics_topics_matrix = full(sp_topics(:,docs_main_data) * sp_topics_found');
display(main_topics_topics_matrix);

%% Perform classification into clusters of 'new' data, and compare to original topics
load(NEW_FILENAME, 'theta')

[~, docs_most_likely_topics] = max(theta, [], 1);

% Display a matrix where the count in entry (i,j) is the number of document
% with original topic i and LDA-found topic j.
% Note that topics found by LDA are unordered by nature.
% Note that we need to filter and reorder documents in sp_topics.
N_DOCS_NEW = length(docs_new_data);
sp_topics_found = sparse(docs_most_likely_topics, 1:N_DOCS_NEW, ones(1, N_DOCS_NEW));
new_topics_topics_matrix = full(sp_topics(:,docs_new_data) * sp_topics_found');
display(new_topics_topics_matrix);

%% Remove LDA output files
delete(MAIN_FILENAME);
delete(NEW_FILENAME);
