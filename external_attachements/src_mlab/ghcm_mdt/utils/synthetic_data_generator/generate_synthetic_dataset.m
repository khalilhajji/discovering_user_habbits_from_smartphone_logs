% GENERATE_SYNTEHTIC_DATASET Generate a synthetic dataset of given characteristics
% 
% GENERATE_SYNTEHTIC_DATASET(FILENAME, ALPHA, BETA, Nd, N_DOCS, N_TOPICS, VOC_SIZE)
% 
% This function generates the configuration of a lda model with
% hyperparameters ALPHA and BETA, N_TOPICS topics, N_DOCS documents each of
% which contains Nd tokens, and a vocabulary size VOC_SIZE.
% 
% The configuration is saved in FILENAME, and the saved variables are:
%   phi             VOC_SIZExN_TOPICS matrix
%   theta           N_TOPICSxN_DOCS matrix
%   docs_vector     1xN vector, where N=N_DOCSxNd is the number of tokens
%   words_vector    1xN vector
%   topics_vector 	1xN vector
% 
% INPUT
%   FILENAME        string
%   ALPHA           scalar
%   BETA            scalar
%   Nd              scalar
%   N_DOCS          scalar
%   N_TOPICS        scalar
%   VOC_SIZE        scalar
function generate_synthetic_dataset(FILENAME, ALPHA, BETA, Nd, N_DOCS, N_TOPICS, VOC_SIZE)

phi = rand_dirichlet(N_TOPICS, VOC_SIZE, BETA);
theta = rand_dirichlet(N_DOCS, N_TOPICS, ALPHA);

[docs_vector, words_vector, topics_vector] = generate_docs(...
    phi, theta, Nd); %#ok<ASGLU,NASGU>

save(FILENAME, 'phi', 'theta', 'docs_vector', 'words_vector', 'topics_vector', ...
    'ALPHA', 'BETA', 'Nd', 'N_DOCS', 'N_TOPICS', 'VOC_SIZE');
end


% This function samples topics and words according to the topic proportions
% in documents, and to the topics distributions over words.
% 
% INPUT
%   phi             VOC_SIZExN_TOPICS matrix
%   theta           N_DOCSxN_TOPICS matrix
%   Nd              scalar
% 
% OUTPUT
%   docs_vector     1xN vector
%   words_vector    1xN vector
%   topics_vector   1xN vector
function [docs_vector, words_vector, topics_vector] = generate_docs(...
    phi, theta, Nd)

N_DOCS = size(theta, 2);
N_TOKENS  = N_DOCS * Nd;

docs_vector = zeros(N_TOKENS, 1);
words_vector = zeros(N_TOKENS, 1);
topics_vector = zeros(N_TOKENS, 1);

% Generate a topic and then a word for each token (associated with a doc)
% (=> produces 3 vectors: doc-topic-word association)
for d=1:N_DOCS
    for i=1:Nd
        j = (d-1)*Nd + i; % Absolute token index (from 1 to n_docs*n_tokens_per_doc)
        
        docs_vector(j) = d;
        
        % Generate a topic according to the topics proportions for doc d
        t = rand_categorical(theta(:,d));
        topics_vector(j) = t;
        
        % Generate a word according to the topic distrib for topic t
        words_vector(j) = rand_categorical(phi(:,t));
    end
end
end
