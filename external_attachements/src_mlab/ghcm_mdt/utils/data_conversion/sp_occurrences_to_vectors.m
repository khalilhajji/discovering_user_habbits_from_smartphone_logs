% Convert a sparse matrix of number of occurrences to matched vectors with
% (doc, term) appearing according to its number of occurences
% 
% [docs_vector, words_vector] = SP_OCCURRENCES_TO_VECTORS(sp_occurrences)
%
% E.g. if T = 3 terms, D = 4 documents
%   sp_occurrences = sparse([1 0 2 0; ...
%                            0 1 0 0; ...
%                            0 0 0 1]); 
% Then
%   docs_vector =  [1 2 3 3 4]'
%   words_vector = [1 2 1 1 3]'
% 
% For speed reason, the element duplication is done in c. The mex file can
% be compiled by running:
%   mex generate_replicated_vectors.c
% 
% INPUT
%   sp_occurrences  VOC_SIZExN_DOCS sparse matrix
% 
% OUTPUT
%   words_vector    N_TOKENSx1 vector
%   docs_vector     N_TOKENSx1 vector
function [docs_vector, words_vector] = sp_occurrences_to_vectors(sp_occurrences)
    
[words, docs, n_occ] = find(sp_occurrences);

N_TOKENS = sum(n_occ);

[docs_vector, words_vector] = generate_replicated_vectors(docs, words, n_occ, N_TOKENS);
end
