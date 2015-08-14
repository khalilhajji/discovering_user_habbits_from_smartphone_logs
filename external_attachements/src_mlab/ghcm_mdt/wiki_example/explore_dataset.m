% ### PART 1 ###
% 
% Before trying to fit the dataset, the first things to do is to visualize
% it, in order to grasp it intuitively and check whether model assumptions
% are satisfied.
% "If LDA doesn't seems like an intuitive way to model, then it probably
% won't work."

% The dataset 'wiki_toy_dataset' has been produced by 
% - lemmatizing wikipedia articles
% - removing a given list of stopwords
% - chosing only a few categories (= topics) and keeping only corresponding
%   articles
% - reducing the vocabulary size, by keeping the most frequent words (in
%   the kept articles)

% The dataset contains:
% - sp_occurrences: VOC_SIZE x N_DOCS sparse matrix, where entry (w,d) is
%   the number of occurrences of word w in document d.
% - sp_topics: N_TOPICS x N_DOCS sparse matrix, where entry (k,d) is 1 if
%   document d is about topic k and 0 otherwise. Note that a document can
%   have several topics.
% - vocabulary: VOC_SIZE x 1 cell array of strings
% - docs_names: N_DOCS x 1 cell array of strings
% - topics_names: N_TOPICS x 1 cell array of strings

%% Start by adding neccessary folder of the LDA_toolbox to the path 
addpath(genpath('../utils')); 
addpath('../LDA_fitting'); 

%% Load the data and display some characteristics
INPUT_FILE = 'wiki_toy_dataset5.mat';
load(INPUT_FILE);

fprintf('The dataset contains %d documents with a vocabulary of size %d.\n', ...
    N_DOCS, VOC_SIZE);
fprintf('In total, there are %d tokens.\n', full(sum(sum(sp_occurrences))));
fprintf('As an example dataset, we know that it contains %d topics.\n', N_TOPICS);

%% Explore the data: most common words in some documents
DOCS_TO_WRITE = 1:10;

display_docs(sp_occurrences, vocabulary, DOCS_TO_WRITE, docs_names(DOCS_TO_WRITE))

%% Explore the data: most common words in each topic
TOPICS_TO_WRITE = 1:N_TOPICS;

% Build count matrix of how many times a word appear in a topic, over docs
words_counts = zeros(VOC_SIZE, N_TOPICS); 
for doc = 1:N_DOCS
    % Find to which topic the document is associated (Here each doc has only one topic)
    doc_topic = find(sp_topics(:, doc), 1);
    % Add the number of words occurrences to this topic
    words_counts(:,doc_topic) = words_counts(:,doc_topic) + sp_occurrences(:, doc);
end

display_words_counts(words_counts, vocabulary, TOPICS_TO_WRITE, topics_names)

% Find words which appear at least once in each topic
words_at_least_once = find(min(words_counts, [], 2) >= 1);
fprintf('%d out of %d words appear at least once in each topic\n', ...
    length(words_at_least_once), length(vocabulary));

%% Estimate the beta parameter (sparsity of words in topics)
beta_mle = estimate_dirichlet_mle(words_counts);
fprintf('The maximum likelihood estimator for beta based on words_counts is %f\n', ...
    beta_mle);

%% Display phi (topics distributions) when using optimal beta
phi = estimate_phi(words_counts, beta_mle);
display_phi(phi, vocabulary, TOPICS_TO_WRITE, topics_names)
