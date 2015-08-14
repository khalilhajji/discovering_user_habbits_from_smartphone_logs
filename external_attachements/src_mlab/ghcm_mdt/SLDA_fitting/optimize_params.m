% INPUT
%   rated_docs: 1xD boolean vector
%   ratings: 1xD vector
%   doc_topic_counts: (sparse) DxK
function [eta, sigma] = optimize_params(rated_docs, ratings, doc_topic_counts)
EPSILON = 0.001; % TODO
fprintf('EPSILON = %f\n', EPSILON);

rated_docs = (rated_docs ~= 0);

Dp = sum(rated_docs);
if(Dp == 0)
    error('No rated documents');
end

% Transpose for quick access to document
doc_topic_counts_t = doc_topic_counts';

% Only keep documents rated and transpose again
A = full(doc_topic_counts_t(:, rated_docs))'; % D'xK

% Normalize!!!
if(sum(sum(A, 2) == 0) ~= 0)
    error('Some documents seem empty!')
end
A = bsxfun(@rdivide, A, sum(A, 2));

% Only keep relevant ratings
y = ratings(rated_docs)'; % D'x1

% Compute optimal parameters
eta = A \ y;

sigma = 1/Dp * sum((y-A*eta).^2) + EPSILON;

end