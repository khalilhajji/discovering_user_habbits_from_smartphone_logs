% Obtain counts from words_vector, docs_vector, topics_vector
% 
% [words_counts, docs_counts] = compute_counts(...
%     words_vector, docs_vector, topics_vector, N_TOPICS, VOC_SIZE, N_DOCS)
% 
% For example, if 
%   words_vector =  [1 2 1 3 4 2]'
%   docs_vector =   [1 1 1 2 2 2]'
%   topics_vector = [2 2 2 1 1 1]'
% Then
%   words_counts =  [0 2; ...
%                    1 1; ...
%                    1 0; ...
%                    1 0]
%   docs_counts =   [0 3; ...
%                    3 0]
% 
% INPUT
%   words_vector    N_TOKENSx1 vector
%   docs_vector     N_TOKENSx1 vector
%   topics_vector   N_TOKENSx1 vector
%   N_TOPICS        scalar
%   [VOC_SIZE]      scalar, optional
%   [N_DOCS]        scalar, optional
% 
% OUTPUT
%   words_counts    VOC_SIZExN_TOPICS sparse matrix
%   docs_counts     N_DOCSxN_TOPICS sparse matrix
function [words_counts, docs_counts] = compute_counts(...
    words_vector, docs_vector, topics_vector, N_TOPICS, VOC_SIZE, N_DOCS)

N_TOKENS = length(words_vector);
if(size(words_vector, 1)~= N_TOKENS || size(docs_vector, 1)~= N_TOKENS ||size(topics_vector, 1)~= N_TOKENS)
    error('Input dont have proper dimensions');
end

if(nargin == 4)
    VOC_SIZE = max(words_vector);
    N_DOCS = max(docs_vector);
end

words_counts = spconvert([[words_vector topics_vector ones(N_TOKENS, 1)]; ...
    VOC_SIZE N_TOPICS 0]);

docs_counts = spconvert([[docs_vector topics_vector ones(N_TOKENS, 1)]; ...
    N_DOCS N_TOPICS 0]);

end
