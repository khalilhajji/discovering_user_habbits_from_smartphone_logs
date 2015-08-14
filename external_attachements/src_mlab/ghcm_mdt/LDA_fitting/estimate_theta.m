% ESTIMATE_THETA Estimate theta based on docs_counts matrix
% 
% theta = estimate_theta(docs_counts, ALPHA)
% 
% LDA recall: phi describes the distribution of words in a topics, while
% theta represents the proportions of topics in a document.
% 
% See also ESTIMATE_ROBUST_THETA
% 
% INPUT
%   docs_counts     N_DOCSxN_TOPICS sparse matrix
%   ALPHA           scalar
% 
% OUTPUT
%   theta           N_TOPICSxN_DOCS matrix
function theta = estimate_theta(docs_counts, ALPHA)

N_TOPICS = size(docs_counts, 2);

docs_counts_sums = sum(docs_counts, 2); % Count of tokens in each doc

theta = ((docs_counts + ALPHA) ./ ...
    (repmat(docs_counts_sums, 1, N_TOPICS) + N_TOPICS * ALPHA))';
end