% ESTIMATE_PHI Estimate phi based on words_counts matrix
% 
% phi = estimate_phi(words_counts, BETA)
% 
% LDA recall: phi describes the distribution of words in a topics, while
% theta represents the proportions of topics in a document.
% 
% See also ESTIMATE_ROBUST_PHI
% 
% INPUT
%   words_counts    VOC_SIZExN_TOPICS sparse matrix
%   BETA            scalar
% 
% OUTPUT
%   phi             VOC_SIZExN_TOPICS matrix
function phi = estimate_phi(words_counts, BETA)

VOC_SIZE = size(words_counts, 1);

topics_counts_sums = sum(words_counts, 1); % Count of tokens in each topic

phi = (words_counts + BETA) ./ ...
    (repmat(topics_counts_sums, VOC_SIZE, 1) + VOC_SIZE * BETA);

% If some topic don't have any observed tokens, then all words are equally
% likely (note that this case shouldn't happen when using a reasonable
% number of topics, and a large enough dataset)
phi(:, topics_counts_sums==0) = 1/VOC_SIZE; 

end