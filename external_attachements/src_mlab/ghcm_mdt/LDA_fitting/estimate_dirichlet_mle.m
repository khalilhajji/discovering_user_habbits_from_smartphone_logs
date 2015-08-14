% alpha = estimate_dirichlet_mle(counts, PRECISION)
% 
% This function find (approximate) the MLE of multinomial samples generated 
% with dirichlet samples, i.e. 
%   counts_1, ..., counts_N_SAMPLES s.t. counts_i ~ Multinomial(theta_i)
%   and theta_1, ..., theta_N_SAMPLES ~ Dirichlet(alpha)
% 
% This can be used:
%   - To find hyperparameter alpha from the docs_counts^T (i.e. what is the
%     sparsity given the topics (realisations) observed in documents)
%   - To find hyperparameter beta from the words_counts (i.e. what is the
%     sparsity given the words (realisations) observed in topics)
% 
% Note that the estimation is more robust when more documents are used.
% 
% INPUT
%   counts      N_DIMSxNSAMPLES matrix (=> N_TOPICSxN_DOCS or VOC_SIZExN_TOPICS)
%   PRECISION   scalar, optional
% 
% OUTPUT
%   alpha       scalar
function alpha = estimate_dirichlet_mle(counts, PRECISION)
if(~exist('PRECISION', 'var'))
    PRECISION = 1e-2;
end

ALPHA_MIN_START = 1e-10;
ALPHA_MAX_START = 1;

% Initialize some interval
alpha_min = ALPHA_MIN_START;
alpha_max = ALPHA_MAX_START;

% Check whether a root of the likelihood equation is contained in the
% interval
% We should have a positive derivative before the root, and a negative after
sign_min = compute_sign(alpha_min, counts);
sign_max = compute_sign(alpha_max, counts);
if(sign_min ~= 1) % The derivative should be positive befor the root
    warning('dirichlet mle seems to be smaller than %f, returning %f', alpha_min, alpha_min)
    alpha = alpha_min;
    return;
elseif(sign_max ~= -1) % The derivative should be negative befor the root
    warning('dirichlet mle seems to be larger than %f, returning %f', alpha_max, alpha_max)
    alpha = alpha_max;
    return;
end

% Use the bisection method until the desired precision is reached
while(alpha_max-alpha_min > PRECISION*2)
    mid_alpha = (alpha_max+alpha_min)/2;
    
    sign_mid_alpha = compute_sign(mid_alpha, counts);
    
    if(sign_mid_alpha == 1) % If still a positive derivative, root is after
        alpha_min = mid_alpha;
    else
        alpha_max = mid_alpha;
    end
end

% Return the midpoint of the interval
alpha = (alpha_max+alpha_min)/2;

end

% Compute the sign of the derivative of the log-likelihood, evaluated at
% alpha
% When often called, psi(alpha+counts) requires lot of time
function s = compute_sign(alpha, counts)
[N_DIMS, N_SAMPLES] = size(counts);

value = N_SAMPLES*N_DIMS*psi(N_DIMS*alpha) - N_SAMPLES*N_DIMS*psi(alpha) + ...
    sum(sum(psi(alpha+counts))) - N_DIMS*sum(psi(N_DIMS*alpha + sum(counts,1)));

s = sign(value);
end

% Debugging function to see what happen in the optimization
% (plot the derivative of the log-likelihood, from which we want the root)
function plot_ll_derivative(counts, alpha_min, alpha_max)
N_POINTS = 1000;
alphas = alpha_min:((alpha_max-alpha_min)/(N_POINTS-1)):alpha_max;

[N_DIMS, N_SAMPLES] = size(counts);

values = zeros(1, N_POINTS);
for i = 1:N_POINTS
    alpha = alphas(i);
    
    values(i) = N_SAMPLES*N_DIMS*psi(N_DIMS*alpha) - N_SAMPLES*N_DIMS*psi(alpha) + ...
        sum(sum(psi(alpha+counts))) - N_DIMS*sum(psi(N_DIMS*alpha + sum(counts,1)));
end

plot(alphas, values);

end
