% For each document, find dominant topic(s)
% 
% sp_topics_found = theta_to_sp_topics(theta, THRESHOLD)
% 
% INPUT
%   theta               N_TOPICS x N_DOCS matrix
%   THRESHOLD           scalar (in (0 1]), optional
% 
% OUTPUT
%   sp_topics_found     N_TOPICS x N_DOCS sparse matrix
function sp_topics_found = theta_to_sp_topics(theta, THRESHOLD)
% TODO: threshold (compared to dominant topic in doc) for following topics

if(exist('THRESHOLD', 'var'))
    error('Threshold not yet implemented')
end

N_DOCS = size(theta, 2);

[~, docs_most_likely_topics] = max(theta, [], 1);

sp_topics_found = sparse(docs_most_likely_topics, 1:N_DOCS, ones(1, N_DOCS));

end
