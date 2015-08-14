% Generate a number according to the categories probabilities, in the set
% {1, ..., N_CATEGORIES}.
% 
% [r] = RAND_CATEGORICAL(probas)
% 
% INPUT
%   probas  <N_CATEGORIES>x1 vector
% 
% OUTPUT
%   r       scalar
function [r] = rand_categorical(probas)
cum_probas = cumsum(probas);
% assert(abs(cum_probas(length(cum_probas)) - 1) < 0.0001) % Safety check (with precision error tolerance)

rand_uniform = rand(1);
r = find(cum_probas >= rand_uniform, 1, 'first');

end
