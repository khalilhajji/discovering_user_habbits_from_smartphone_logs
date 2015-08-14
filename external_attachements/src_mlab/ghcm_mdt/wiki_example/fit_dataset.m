% ### PART 2 ###
% 
% Convert data, fit the model, display the topic, show how documents have 
% been reclustered, show 'pure'/'mixed' documents examples

%% Start by adding neccessary folder of the LDA_toolbox to the path 
addpath(genpath('../utils')); 
addpath('../LDA_fitting'); 

%% Load the data and convert to vector format
INPUT_FILE = 'wiki_toy_dataset5.mat';
load(INPUT_FILE);

[docs_vector, words_vector] = sp_occurrences_to_vectors(sp_occurrences);

%% Fit LDA
OUTPUT_FILENAME = 'lda_output_for_wiki_toy.mat';

PARAMS.N_TOPICS = 5;
PARAMS.MAX_ITERS = 10; % Enough for a small dataset

fit_LDA_advanced(docs_vector, words_vector, OUTPUT_FILENAME, PARAMS)

%% Load the results and display the topic
load(OUTPUT_FILENAME, 'phi', 'theta')

TOPICS_TO_WRITE = 1:N_TOPICS;
display_phi(phi, vocabulary, TOPICS_TO_WRITE)

%% Perform classification into clusters and compare to original topics
[~, docs_most_likely_topics] = max(theta, [], 1);

% Display a matrix where the count in entry (i,j) is the number of document
% with original topic i and LDA-found topic j.
% Note that topics found by LDA are unordered by nature.
sp_topics_found = sparse(docs_most_likely_topics, 1:N_DOCS, ones(1, N_DOCS));
topics_topics_matrix = full(sp_topics * sp_topics_found');
display(topics_topics_matrix);

%% Show documents very close to each topic
N_DOCS_TO_WRITE = 5;

clc;
for topic = 1:N_TOPICS
    % Print the topic before printing its representative documents
    fprintf('\n##################################################\n')
    display_phi(phi, vocabulary, topic);
    
    % Find the most representative documents (those containing the highest
    % probability of the given topic)
    [~, docs_indices_by_purity] = sort(theta(topic,:), 'descend');
    docs_to_write = docs_indices_by_purity(1:N_DOCS_TO_WRITE);
    
    % Display these documents
    display_docs(sp_occurrences, vocabulary, docs_to_write, docs_names(docs_to_write));
end

%% Show documents inbetween topics
N_DOCS_TO_WRITE = 10;

% Find documents where the second topic has highest proportions, i.e. we
% are looking for documents containing 2 dominant topics
sorted_theta = sort(theta, 1, 'descend');
[~, docs_indices_by_2nd_topic] = sort(sorted_theta(2,:), 'descend');
docs_to_write = docs_indices_by_2nd_topic(1:N_DOCS_TO_WRITE);

clc;
for i = 1:N_DOCS_TO_WRITE
    % Display one document of the documents previously selected
    doc = docs_to_write(i);
    
    fprintf('\n##################################################\n')
    display_docs(sp_occurrences, vocabulary, doc, docs_names(doc));
    
    % Find and display which are the main topics of this document
    [doc_sorted_theta, sorted_topics_indices] = sort(theta(:,doc), 'descend');
    
    fprintf('Document main topics: topic %d: %f, topic %d: %f\n\n', ...
        sorted_topics_indices(1), doc_sorted_theta(1), sorted_topics_indices(2), doc_sorted_theta(2));

    display_phi(phi, vocabulary, sorted_topics_indices(1));
    display_phi(phi, vocabulary, sorted_topics_indices(2));
end


%% Remove LDA output file
%delete(OUTPUT_FILENAME);
